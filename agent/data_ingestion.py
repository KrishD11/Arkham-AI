"""Data ingestion service for fetching risk data from external APIs"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from agent.config import Config

logger = logging.getLogger(__name__)


@dataclass
class RiskDataPoint:
    """Single risk data point"""
    source: str
    category: str  # 'trade_news', 'political', 'port_congestion'
    title: str
    description: str
    severity: float  # 0.0 to 1.0
    location: str
    timestamp: datetime
    metadata: Dict[str, Any]


class DataIngestionService:
    """Service for ingesting risk data from various sources"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize data ingestion service"""
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"{self.config.AGENT_NAME}/1.0"
        })
        
        # Initialize database service for storing data
        try:
            from agent.database import get_database_service
            self.db_service = get_database_service()
        except Exception as e:
            logger.warning(f"Could not initialize database service: {e}")
            self.db_service = None
    
    def fetch_trade_news(self, region: Optional[str] = None, limit: int = 50) -> List[RiskDataPoint]:
        """Fetch trade news and disruptions"""
        try:
            # Use real API if key is configured
            if self.config.TRADE_NEWS_API_KEY:
                data_points = self._fetch_trade_news_api(region, limit)
            else:
                # Fallback to mock data
                logger.info("TRADE_NEWS_API_KEY not configured, using mock data")
                data_points = self._fetch_trade_news_mock(region, limit)
            
            # Store in MongoDB if available
            if self.db_service and self.db_service.is_connected() and data_points:
                self.db_service.insert_risk_data(data_points)
            
            return data_points
        except Exception as e:
            logger.error(f"Error fetching trade news: {e}")
            # Fallback to mock on error
            return self._fetch_trade_news_mock(region, limit)
    
    def fetch_political_instability(self, region: Optional[str] = None) -> List[RiskDataPoint]:
        """Fetch political instability and geopolitical risks"""
        try:
            # Try to use ACLED API if credentials are available
            if self.config.ACLED_USERNAME and self.config.ACLED_PASSWORD:
                data_points = self._fetch_political_instability_acled(region)
            else:
                # Fallback to mock data
                logger.info("ACLED credentials not configured, using mock data")
                data_points = self._fetch_political_instability_mock(region)
            
            # Store in MongoDB if available
            if self.db_service and self.db_service.is_connected() and data_points:
                self.db_service.insert_risk_data(data_points)
            
            return data_points
        except Exception as e:
            logger.error(f"Error fetching political instability: {e}")
            # Fallback to mock data on error
            return self._fetch_political_instability_mock(region)
    
    def fetch_port_congestion(self, port_code: Optional[str] = None) -> List[RiskDataPoint]:
        """Fetch port congestion and operational status"""
        try:
            # TODO: Replace with real API when available
            # Example: Port API, shipping data API, or custom logistics API
            data_points = self._fetch_port_congestion_mock(port_code)
            
            # Store in MongoDB if available
            if self.db_service and self.db_service.is_connected() and data_points:
                self.db_service.insert_risk_data(data_points)
            
            return data_points
        except Exception as e:
            logger.error(f"Error fetching port congestion: {e}")
            return []
    
    def fetch_all_risk_data(
        self, 
        region: Optional[str] = None,
        port_code: Optional[str] = None
    ) -> List[RiskDataPoint]:
        """Fetch all risk data from all sources"""
        all_data = []
        
        # Fetch from all sources in parallel (can be optimized with async)
        all_data.extend(self.fetch_trade_news(region))
        all_data.extend(self.fetch_political_instability(region))
        all_data.extend(self.fetch_port_congestion(port_code))
        
        # Sort by timestamp (most recent first)
        all_data.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"Fetched {len(all_data)} risk data points")
        return all_data
    
    def fetch_risk_data_for_route(
        self, 
        origin: str, 
        destination: str,
        route_regions: Optional[List[str]] = None
    ) -> List[RiskDataPoint]:
        """Fetch risk data specific to a shipping route"""
        all_data = []
        
        # Extract regions from port names and route regions
        regions_to_check = set()
        
        # Extract country/region from port names
        origin_region = self._extract_region_from_port(origin)
        dest_region = self._extract_region_from_port(destination)
        
        if origin_region:
            regions_to_check.add(origin_region)
        if dest_region:
            regions_to_check.add(dest_region)
        
        # Add explicit route regions
        if route_regions:
            regions_to_check.update(route_regions)
        
        # Fetch data for all identified regions
        for region in regions_to_check:
            if region:
                all_data.extend(self.fetch_trade_news(region, limit=20))
                all_data.extend(self.fetch_political_instability(region))
        
        # Fetch port-specific data
        origin_port_code = self._extract_port_code(origin)
        dest_port_code = self._extract_port_code(destination)
        
        if origin_port_code:
            all_data.extend(self.fetch_port_congestion(origin_port_code))
        if dest_port_code:
            all_data.extend(self.fetch_port_congestion(dest_port_code))
        
        # Also fetch general trade data for the route
        all_data.extend(self.fetch_trade_news(None, limit=30))
        
        # Sort by timestamp (most recent first)
        all_data.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"Fetched {len(all_data)} risk data points for route {origin} -> {destination}")
        return all_data
    
    def _extract_region_from_port(self, port_name: str) -> Optional[str]:
        """Extract region/country from port name"""
        if not port_name:
            return None
        
        port_name_lower = port_name.lower()
        
        # Map port names to regions/countries
        port_to_region = {
            # Asia-Pacific
            'taipei': 'taiwan',
            'taiwan': 'taiwan',
            'shanghai': 'china',
            'shenzhen': 'china',
            'hong kong': 'china',
            'singapore': 'singapore',
            'busan': 'south korea',
            'tokyo': 'japan',
            'yokohama': 'japan',
            'ho chi minh': 'vietnam',
            'vietnam': 'vietnam',
            'bangkok': 'thailand',
            'jakarta': 'indonesia',
            'manila': 'philippines',
            'mumbai': 'india',
            'chennai': 'india',
            
            # Middle East
            'dubai': 'uae',
            'jeddah': 'saudi arabia',
            
            # Europe
            'rotterdam': 'netherlands',
            'hamburg': 'germany',
            'antwerp': 'belgium',
            'london': 'uk',
            'felixstowe': 'uk',
            'le havre': 'france',
            'genoa': 'italy',
            'barcelona': 'spain',
            'piraeus': 'greece',
            
            # North America
            'los angeles': 'usa',
            'long beach': 'usa',
            'new york': 'usa',
            'newark': 'usa',
            'savannah': 'usa',
            'charleston': 'usa',
            'houston': 'usa',
            'vancouver': 'canada',
            
            # South America
            'santos': 'brazil',
            'buenos aires': 'argentina',
            'callao': 'peru',
            
            # Africa
            'durban': 'south africa',
            'cape town': 'south africa',
            'lagos': 'nigeria',
        }
        
        # Check for matches
        for key, region in port_to_region.items():
            if key in port_name_lower:
                return region
        
        # Try to extract country from "Port of X, Country" format
        if ',' in port_name:
            parts = port_name.split(',')
            if len(parts) > 1:
                country = parts[-1].strip().lower()
                # Map common country names
                country_map = {
                    'usa': 'usa',
                    'united states': 'usa',
                    'china': 'china',
                    'japan': 'japan',
                    'south korea': 'south korea',
                    'taiwan': 'taiwan',
                    'vietnam': 'vietnam',
                    'singapore': 'singapore',
                    'thailand': 'thailand',
                    'indonesia': 'indonesia',
                    'philippines': 'philippines',
                    'india': 'india',
                    'uae': 'uae',
                    'saudi arabia': 'saudi arabia',
                    'netherlands': 'netherlands',
                    'germany': 'germany',
                    'belgium': 'belgium',
                    'uk': 'uk',
                    'france': 'france',
                    'italy': 'italy',
                    'spain': 'spain',
                    'greece': 'greece',
                    'canada': 'canada',
                    'brazil': 'brazil',
                    'argentina': 'argentina',
                    'peru': 'peru',
                    'south africa': 'south africa',
                    'nigeria': 'nigeria',
                }
                return country_map.get(country, country)
        
        return None
    
    def _extract_port_code(self, port_name: str) -> Optional[str]:
        """Extract port code from port name if available"""
        # Port codes are typically 5 characters (e.g., USLAX, SGSIN)
        # This is a simplified extraction - in production would use a port database
        port_code_map = {
            'port of los angeles': 'USLAX',
            'port of long beach': 'USLGB',
            'port of new york': 'USNYC',
            'port of singapore': 'SGSIN',
            'port of shanghai': 'CNSHA',
            'port of rotterdam': 'NLRTM',
            'port of hamburg': 'DEHAM',
            'port of busan': 'KRBUS',
            'port of tokyo': 'JPTYO',
        }
        
        port_name_lower = port_name.lower()
        for key, code in port_code_map.items():
            if key in port_name_lower:
                return code
        
        return None
    
    def _fetch_trade_news_api(self, region: Optional[str] = None, limit: int = 50) -> List[RiskDataPoint]:
        """Fetch trade news from US Trade.gov API"""
        try:
            # US Trade.gov API endpoint
            base_url = "https://data.trade.gov"
            # Try search endpoint first, fallback to count if needed
            endpoint = "/trade_leads/v1/search"  # For actual trade leads data
            
            headers = {
                "Content-Type": "application/json"
            }
            
            params = {
                "subscription-key": self.config.TRADE_NEWS_API_KEY,  # Trade.gov uses query parameter
                "size": min(limit, 100),  # Use 'size' parameter instead of 'limit'
                "format": "json"
            }
            
            # Search endpoint requires at least one: q, country_codes, or date ranges
            if region:
                # Map region to country codes if needed
                # Trade.gov uses ISO country codes
                region_to_country_code = {
                    'usa': 'US',
                    'united states': 'US',
                    'china': 'CN',
                    'japan': 'JP',
                    'south korea': 'KR',
                    'taiwan': 'TW',
                    'vietnam': 'VN',
                    'singapore': 'SG',
                    'thailand': 'TH',
                    'indonesia': 'ID',
                    'philippines': 'PH',
                    'india': 'IN',
                    'uae': 'AE',
                    'saudi arabia': 'SA',
                    'netherlands': 'NL',
                    'germany': 'DE',
                    'belgium': 'BE',
                    'uk': 'GB',
                    'france': 'FR',
                    'italy': 'IT',
                    'spain': 'ES',
                    'greece': 'GR',
                    'canada': 'CA',
                    'brazil': 'BR',
                    'argentina': 'AR',
                    'peru': 'PE',
                    'south africa': 'ZA',
                    'nigeria': 'NG',
                }
                country_code = region_to_country_code.get(region.lower(), region.upper()[:2])
                params["country_codes"] = country_code
            else:
                # Use a more specific query for trade disruptions
                params["q"] = "trade disruption OR supply chain OR shipping OR logistics"
            
            response = self.session.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )
            
            # If search endpoint doesn't work, try count endpoint to verify API access
            if response.status_code == 404:
                logger.info("Search endpoint not found, trying count endpoint")
                count_response = self.session.get(
                    f"{base_url}/trade_leads/v1/count",
                    headers=headers,  # Use same headers
                    params={"format": "json"},
                    timeout=10
                )
                if count_response.status_code == 200:
                    logger.info("Count endpoint accessible, but search endpoint needed for data")
                    # Return empty list - count endpoint doesn't provide trade leads data
                    return []
            
            if response.status_code == 200:
                data = response.json()
                risk_points = []
                
                # Parse API response - Trade.gov returns {"results": [...]}
                articles = data.get("results", [])
                
                for article in articles[:limit]:
                    # Extract fields from Trade.gov API response structure
                    title = article.get("title", "Trade Lead Update")
                    description = article.get("description", "")
                    location = article.get("country_code", "Unknown")
                    
                    # Parse timestamp - Trade.gov uses published_date
                    timestamp_str = article.get("published_date")
                    if timestamp_str:
                        try:
                            # Trade.gov uses YYYY-MM-DD format
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d')
                        except:
                            timestamp = datetime.now()
                    else:
                        timestamp = datetime.now()
                    
                    # Calculate severity based on dates and urgency
                    # More recent = higher severity, approaching deadlines = higher severity
                    severity = 0.5  # Default
                    
                    # Check if tender/contract dates are approaching
                    tender_end = article.get("tender_end_date")
                    contract_start = article.get("contract_start_date")
                    
                    if tender_end:
                        try:
                            tender_end_date = datetime.strptime(tender_end, '%Y-%m-%d')
                            days_until = (tender_end_date - datetime.now()).days
                            if 0 <= days_until <= 7:  # Deadline within a week
                                severity = 0.8
                            elif 8 <= days_until <= 30:  # Deadline within a month
                                severity = 0.6
                        except:
                            pass
                    
                    # Adjust based on recency
                    days_old = (datetime.now() - timestamp).days
                    if days_old <= 1:
                        severity = min(1.0, severity + 0.2)
                    elif days_old <= 7:
                        severity = min(1.0, severity + 0.1)
                    
                    severity = max(0.0, min(1.0, severity))  # Clamp between 0 and 1
                    
                    risk_points.append(RiskDataPoint(
                        source="trade_gov_api",
                        category="trade_news",
                        title=title,
                        description=description[:500],  # Limit description length
                        severity=severity,
                        location=location,
                        timestamp=timestamp,
                        metadata={
                            "article_id": article.get("id"),
                            "source": "US Trade.gov",
                            "url": article.get("url"),
                            "country_code": article.get("country_code"),
                            "tender_start_date": article.get("tender_start_date"),
                            "tender_end_date": article.get("tender_end_date"),
                            "contract_start_date": article.get("contract_start_date"),
                            "contract_end_date": article.get("contract_end_date"),
                            "raw_data": article
                        }
                    ))
                
                logger.info(f"Fetched {len(risk_points)} trade news articles from Trade.gov API")
                return risk_points
            else:
                logger.warning(f"Trade News API returned status {response.status_code}: {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching trade news from API: {e}")
            raise
    
    # Mock data methods for MVP
    def _fetch_trade_news_mock(self, region: Optional[str] = None, limit: int = 50) -> List[RiskDataPoint]:
        """Mock trade news data"""
        mock_news = [
            RiskDataPoint(
                source="trade_news_api",
                category="trade_news",
                title="New Tariffs Announced on Semiconductor Imports",
                description="Trade tensions escalate with new tariffs affecting semiconductor supply chains",
                severity=0.75,
                location="Taiwan Strait",
                timestamp=datetime.now() - timedelta(hours=2),
                metadata={"impact": "high", "sector": "semiconductors"}
            ),
            RiskDataPoint(
                source="trade_news_api",
                category="trade_news",
                title="Supply Chain Disruption in South China Sea",
                description="Increased shipping delays due to regional tensions",
                severity=0.65,
                location="South China Sea",
                timestamp=datetime.now() - timedelta(hours=5),
                metadata={"impact": "medium", "sector": "shipping"}
            ),
            RiskDataPoint(
                source="trade_news_api",
                category="trade_news",
                title="Trade Agreement Updates",
                description="Positive developments in regional trade agreements",
                severity=0.25,
                location="Southeast Asia",
                timestamp=datetime.now() - timedelta(days=1),
                metadata={"impact": "low", "sector": "general"}
            ),
        ]
        
        if region:
            mock_news = [n for n in mock_news if region.lower() in n.location.lower()]
        
        return mock_news[:limit]
    
    def _fetch_political_instability_acled(self, region: Optional[str] = None) -> List[RiskDataPoint]:
        """Fetch political instability data from ACLED API"""
        try:
            from agent.policy import get_acled_auth_policy
            
            acled_policy = get_acled_auth_policy()
            
            # Map region to country names (simplified - in production would be more comprehensive)
            country = None
            if region:
                region_to_country = {
                    "asia": None,  # Would need multiple countries
                    "asia-pacific": None,
                    "south china sea": "China",
                    "east china sea": "China",
                    "taiwan": "Taiwan",
                    "vietnam": "Vietnam",
                    "japan": "Japan",
                    "singapore": "Singapore",
                }
                country = region_to_country.get(region.lower())
            
            # Get recent events (last 30 days)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            event_date = f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}"
            
            # Fetch ACLED data
            params = {
                "event_date": event_date,
                "event_date_where": "BETWEEN",
                "fields": "event_id_cnty|event_date|event_type|sub_event_type|country|admin1|location|fatalities|notes",
                "limit": 100
            }
            
            if country:
                params["country"] = country
            
            data = acled_policy.fetch_acled_data(
                endpoint="acled/read",
                **params
            )
            
            # Convert ACLED events to RiskDataPoints
            risk_points = []
            if data.get("status") == 200 and "data" in data:
                for event in data["data"]:
                    # Calculate severity based on event type and fatalities
                    severity = self._calculate_acled_severity(event)
                    
                    # Parse event date
                    try:
                        event_date = datetime.strptime(event.get("event_date", ""), "%Y-%m-%d")
                    except:
                        event_date = datetime.now()
                    
                    risk_points.append(RiskDataPoint(
                        source="acled_api",
                        category="political",
                        title=f"{event.get('event_type', 'Event')} - {event.get('sub_event_type', '')}",
                        description=event.get("notes", "")[:200] or f"Event in {event.get('location', 'Unknown')}",
                        severity=severity,
                        location=f"{event.get('country', '')}, {event.get('admin1', '')}, {event.get('location', '')}",
                        timestamp=event_date,
                        metadata={
                            "event_id": event.get("event_id_cnty"),
                            "event_type": event.get("event_type"),
                            "sub_event_type": event.get("sub_event_type"),
                            "fatalities": event.get("fatalities", 0),
                            "country": event.get("country"),
                            "admin1": event.get("admin1")
                        }
                    ))
            
            logger.info(f"Fetched {len(risk_points)} political instability events from ACLED")
            return risk_points
            
        except Exception as e:
            logger.error(f"Error fetching ACLED data: {e}")
            raise
    
    def _calculate_acled_severity(self, event: Dict[str, Any]) -> float:
        """Calculate severity score from ACLED event"""
        base_severity = 0.3
        
        # Increase severity based on event type
        event_type = event.get("event_type", "").lower()
        sub_event_type = event.get("sub_event_type", "").lower()
        
        if "violence" in event_type or "violence" in sub_event_type:
            base_severity += 0.3
        elif "battle" in event_type or "battle" in sub_event_type:
            base_severity += 0.4
        elif "explosion" in event_type or "explosion" in sub_event_type:
            base_severity += 0.35
        elif "protest" in event_type or "protest" in sub_event_type:
            base_severity += 0.1
        
        # Increase severity based on fatalities
        fatalities = int(event.get("fatalities", 0) or 0)
        if fatalities > 0:
            if fatalities >= 100:
                base_severity += 0.3
            elif fatalities >= 10:
                base_severity += 0.2
            elif fatalities >= 1:
                base_severity += 0.1
        
        return min(1.0, base_severity)
    
    def _fetch_political_instability_mock(self, region: Optional[str] = None) -> List[RiskDataPoint]:
        """Mock political instability data"""
        mock_political = [
            RiskDataPoint(
                source="geopolitical_api",
                category="political",
                title="Increased Military Activity in Region",
                description="Heightened military presence affecting shipping lanes",
                severity=0.70,
                location="East China Sea",
                timestamp=datetime.now() - timedelta(hours=3),
                metadata={"type": "military", "duration": "ongoing"}
            ),
            RiskDataPoint(
                source="geopolitical_api",
                category="political",
                title="Diplomatic Tensions Rising",
                description="Escalating diplomatic tensions between regional powers",
                severity=0.60,
                location="Asia-Pacific",
                timestamp=datetime.now() - timedelta(days=1),
                metadata={"type": "diplomatic", "duration": "recent"}
            ),
            RiskDataPoint(
                source="geopolitical_api",
                category="political",
                title="Stable Political Environment",
                description="No significant political disruptions reported",
                severity=0.20,
                location="Japan",
                timestamp=datetime.now() - timedelta(hours=12),
                metadata={"type": "stability", "duration": "stable"}
            ),
        ]
        
        if region:
            mock_political = [p for p in mock_political if region.lower() in p.location.lower()]
        
        return mock_political
    
    def _fetch_port_congestion_mock(self, port_code: Optional[str] = None) -> List[RiskDataPoint]:
        """Mock port congestion data"""
        mock_ports = [
            RiskDataPoint(
                source="port_api",
                category="port_congestion",
                title="High Congestion at Los Angeles Port",
                description="Container backlog causing 3-5 day delays",
                severity=0.55,
                location="Los Angeles, USA",
                timestamp=datetime.now() - timedelta(hours=1),
                metadata={"port_code": "USLAX", "wait_time_days": 4, "capacity": "85%"}
            ),
            RiskDataPoint(
                source="port_api",
                category="port_congestion",
                title="Normal Operations at Singapore Port",
                description="Port operating at normal capacity",
                severity=0.15,
                location="Singapore",
                timestamp=datetime.now() - timedelta(hours=6),
                metadata={"port_code": "SGSIN", "wait_time_days": 0, "capacity": "45%"}
            ),
            RiskDataPoint(
                source="port_api",
                category="port_congestion",
                title="Moderate Delays at Rotterdam",
                description="Slight congestion with 1-2 day delays",
                severity=0.35,
                location="Rotterdam, Netherlands",
                timestamp=datetime.now() - timedelta(hours=4),
                metadata={"port_code": "NLRTM", "wait_time_days": 2, "capacity": "70%"}
            ),
        ]
        
        if port_code:
            mock_ports = [
                p for p in mock_ports 
                if port_code.upper() in p.metadata.get("port_code", "").upper()
            ]
        
        return mock_ports


# Global service instance
_service_instance: Optional[DataIngestionService] = None


def get_data_ingestion_service() -> DataIngestionService:
    """Get or create the global data ingestion service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DataIngestionService()
    return _service_instance

