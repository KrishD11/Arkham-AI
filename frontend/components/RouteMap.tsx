import React, { useMemo, useState, useEffect } from 'react';
import { GoogleMap, LoadScript, Marker, Polyline } from '@react-google-maps/api';
import type { Route, Port } from '../types';

interface RouteMapProps {
    routes: Route[];
    activeRouteId: string;
    riskDataPoints?: Array<{
        location?: string;
        latitude?: number;
        longitude?: number;
        severity?: number;
        category?: string;
        title?: string;
    }>;
}

// Port coordinates cache (fallback if geocoding fails)
// Based on major world ports - coordinates will be geocoded dynamically
const PORT_COORDINATES: Record<string, { lat: number; lng: number }> = {
    // Asia-Pacific
    'Port of Taipei, Taiwan': { lat: 25.0330, lng: 121.5654 },
    'Taiwan': { lat: 25.0330, lng: 121.5654 },
    'Port of Shanghai, China': { lat: 31.2304, lng: 121.4737 },
    'Shanghai': { lat: 31.2304, lng: 121.4737 },
    'Port of Shenzhen, China': { lat: 22.5431, lng: 114.0579 },
    'Port of Singapore, Singapore': { lat: 1.2897, lng: 103.8501 },
    'Singapore': { lat: 1.2897, lng: 103.8501 },
    'Port of Hong Kong, China': { lat: 22.3193, lng: 114.1694 },
    'Port of Busan, South Korea': { lat: 35.1796, lng: 129.0756 },
    'Port of Tokyo, Japan': { lat: 35.6762, lng: 139.6503 },
    'Tokyo': { lat: 35.6762, lng: 139.6503 },
    'Japan': { lat: 35.6762, lng: 139.6503 },
    'Port of Yokohama, Japan': { lat: 35.4437, lng: 139.6380 },
    'Port of Ho Chi Minh City, Vietnam': { lat: 10.7769, lng: 106.7009 },
    'Vietnam': { lat: 10.7769, lng: 106.7009 },
    'Port of Bangkok, Thailand': { lat: 13.7563, lng: 100.5018 },
    'Port of Jakarta, Indonesia': { lat: -6.2088, lng: 106.8456 },
    'Port of Manila, Philippines': { lat: 14.5995, lng: 120.9842 },
    'Port of Mumbai, India': { lat: 19.0760, lng: 72.8777 },
    'Port of Chennai, India': { lat: 13.0827, lng: 80.2707 },
    
    // Middle East
    'Port of Dubai, UAE': { lat: 25.2048, lng: 55.2708 },
    'Port of Jeddah, Saudi Arabia': { lat: 21.4858, lng: 39.1925 },
    
    // Europe
    'Port of Rotterdam, Netherlands': { lat: 51.9225, lng: 4.4792 },
    'Port of Hamburg, Germany': { lat: 53.5511, lng: 9.9937 },
    'Port of Antwerp, Belgium': { lat: 51.2194, lng: 4.4025 },
    'Port of London, UK': { lat: 51.5074, lng: -0.1278 },
    'Port of Felixstowe, UK': { lat: 51.9617, lng: 1.3514 },
    'Port of Le Havre, France': { lat: 49.4944, lng: 0.1079 },
    'Port of Genoa, Italy': { lat: 44.4056, lng: 8.9463 },
    'Port of Barcelona, Spain': { lat: 41.3851, lng: 2.1734 },
    'Port of Piraeus, Greece': { lat: 37.9420, lng: 23.6462 },
    
    // North America
    'Port of Los Angeles, USA': { lat: 33.7490, lng: -118.2648 },
    'Los Angeles': { lat: 33.7490, lng: -118.2648 },
    'Port of Long Beach, USA': { lat: 33.7701, lng: -118.1937 },
    'Port of New York/Newark, USA': { lat: 40.7128, lng: -74.0060 },
    'Port of New York, USA': { lat: 40.7128, lng: -74.0060 },
    'Port of Savannah, USA': { lat: 32.0809, lng: -81.0912 },
    'Port of Charleston, USA': { lat: 32.7765, lng: -79.9311 },
    'Port of Houston, USA': { lat: 29.7604, lng: -95.3698 },
    'Port of Vancouver, Canada': { lat: 49.2827, lng: -123.1207 },
    
    // South America
    'Port of Santos, Brazil': { lat: -23.9608, lng: -46.3336 },
    'Port of Buenos Aires, Argentina': { lat: -34.6037, lng: -58.3816 },
    'Port of Callao, Peru': { lat: -12.0464, lng: -77.0428 },
    
    // Africa
    'Port of Durban, South Africa': { lat: -29.8587, lng: 31.0218 },
    'Port of Cape Town, South Africa': { lat: -33.9249, lng: 18.4241 },
    'Port of Lagos, Nigeria': { lat: 6.5244, lng: 3.3792 },
};

// Geocode a port name using Google Geocoding API
const geocodePort = async (portName: string): Promise<{ lat: number; lng: number } | null> => {
    const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    if (!API_KEY) return null;

    try {
        const response = await fetch(
            `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(portName)}&key=${API_KEY}`
        );
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            const location = data.results[0].geometry.location;
            return { lat: location.lat, lng: location.lng };
        }
    } catch (error) {
        console.warn(`Geocoding failed for ${portName}:`, error);
    }
    
    return null;
};

// Get coordinates for a port (with caching)
const getPortCoordinates = async (portName: string): Promise<{ lat: number; lng: number }> => {
    // Check cache first
    if (PORT_COORDINATES[portName]) {
        return PORT_COORDINATES[portName];
    }

    // Try geocoding
    const coords = await geocodePort(portName);
    if (coords) {
        PORT_COORDINATES[portName] = coords;
        return coords;
    }

    // Fallback to default
    return { lat: 0, lng: 0 };
};

const RouteMap: React.FC<RouteMapProps> = ({ routes, activeRouteId, riskDataPoints = [] }) => {
    const [portCoords, setPortCoords] = useState<Record<string, { lat: number; lng: number }>>({});
    const [isLoadingCoords, setIsLoadingCoords] = useState(true);

    const mapContainerStyle = {
        width: '100%',
        height: '400px',
    };

    // Load port coordinates on mount and when routes change
    useEffect(() => {
        const loadCoordinates = async () => {
            setIsLoadingCoords(true);
            const coords: Record<string, { lat: number; lng: number }> = {};
            
            // Get unique ports from all routes
            const uniquePorts = new Set<string>();
            routes.forEach(route => {
                uniquePorts.add(route.origin.name);
                uniquePorts.add(route.destination.name);
                route.stops?.forEach(stop => uniquePorts.add(stop.name));
            });

            // Geocode all ports
            const coordPromises = Array.from(uniquePorts).map(async (portName) => {
                const coord = await getPortCoordinates(portName);
                return { portName, coord };
            });

            const results = await Promise.all(coordPromises);
            results.forEach(({ portName, coord }) => {
                coords[portName] = coord;
            });

            setPortCoords(coords);
            setIsLoadingCoords(false);
        };

        loadCoordinates();
    }, [routes]);
    
    // Update map when risk data points change
    useEffect(() => {
        console.log('Risk data points updated:', riskDataPoints.length);
    }, [riskDataPoints]);

    const defaultCenter = useMemo(() => {
        if (routes.length > 0 && routes[0].origin) {
            const originName = routes[0].origin.name;
            return portCoords[originName] || PORT_COORDINATES[originName] || { lat: 25.0330, lng: 121.5654 };
        }
        return { lat: 25.0330, lng: 121.5654 }; // Default to Taiwan
    }, [routes, portCoords]);

    const defaultOptions = {
        zoom: 4,
        disableDefaultUI: false,
        zoomControl: true,
        streetViewControl: false,
        mapTypeControl: true,
        fullscreenControl: true,
    };

    // Generate route paths
    const routePaths = useMemo(() => {
        return routes.map(route => {
            const path: { lat: number; lng: number }[] = [];
            
            // Add origin
            const originCoords = portCoords[route.origin.name] || PORT_COORDINATES[route.origin.name];
            if (originCoords && originCoords.lat !== 0 && originCoords.lng !== 0) {
                path.push(originCoords);
            }

            // Add stops
            if (route.stops) {
                route.stops.forEach(stop => {
                    const stopCoords = portCoords[stop.name] || PORT_COORDINATES[stop.name];
                    if (stopCoords && stopCoords.lat !== 0 && stopCoords.lng !== 0) {
                        path.push(stopCoords);
                    }
                });
            }

            // Add destination
            const destCoords = portCoords[route.destination.name] || PORT_COORDINATES[route.destination.name];
            if (destCoords && destCoords.lat !== 0 && destCoords.lng !== 0) {
                path.push(destCoords);
            }

            return path;
        });
    }, [routes, portCoords]);

    // Get route color based on active status
    const getRouteColor = (routeId: string) => {
        if (routeId === activeRouteId) {
            return '#06b6d4'; // cyan-500
        }
        return '#6b7280'; // gray-500
    };

    // Get route opacity
    const getRouteOpacity = (routeId: string) => {
        if (routeId === activeRouteId) {
            return 1.0;
        }
        return 0.4;
    };

    // Get route weight
    const getRouteWeight = (routeId: string) => {
        if (routeId === activeRouteId) {
            return 4;
        }
        return 2;
    };

    // Process risk data points for markers
    const riskMarkers = useMemo(() => {
        return riskDataPoints
            .filter(point => point.latitude && point.longitude)
            .map((point, index) => ({
                id: `risk-${index}`,
                position: { lat: point.latitude!, lng: point.longitude! },
                severity: point.severity || 0.5,
                category: point.category || 'Unknown',
                title: point.title || 'Risk Event',
            }));
    }, [riskDataPoints]);

    // Generate port markers - MUST be before conditional returns!
    const portMarkers = useMemo(() => {
        const uniquePorts = new Map<string, { coords: { lat: number; lng: number }, isActive: boolean, portName: string }>();
        
        // Collect all ports from all routes
        routes.forEach(route => {
            const isActive = route.id === activeRouteId;
            
            // Origin port
            const originCoords = portCoords[route.origin.name] || PORT_COORDINATES[route.origin.name] || PORT_COORDINATES[route.origin.name.split(',')[0]];
            if (originCoords && originCoords.lat !== 0 && originCoords.lng !== 0) {
                const key = `${originCoords.lat.toFixed(4)}-${originCoords.lng.toFixed(4)}`;
                const existing = uniquePorts.get(key);
                if (!existing) {
                    uniquePorts.set(key, {
                        coords: originCoords,
                        isActive: isActive,
                        portName: route.origin.name
                    });
                } else if (isActive) {
                    uniquePorts.set(key, { ...existing, isActive: true });
                }
            }
            
            // Waypoint ports (stops)
            route.stops?.forEach(stop => {
                const stopCoords = portCoords[stop.name] || PORT_COORDINATES[stop.name] || PORT_COORDINATES[stop.name.split(',')[0]];
                if (stopCoords && stopCoords.lat !== 0 && stopCoords.lng !== 0) {
                    const key = `${stopCoords.lat.toFixed(4)}-${stopCoords.lng.toFixed(4)}`;
                    const existing = uniquePorts.get(key);
                    if (!existing) {
                        uniquePorts.set(key, {
                            coords: stopCoords,
                            isActive: isActive,
                            portName: stop.name
                        });
                    } else if (isActive) {
                        uniquePorts.set(key, { ...existing, isActive: true });
                    }
                }
            });
            
            // Destination port
            const destCoords = portCoords[route.destination.name] || PORT_COORDINATES[route.destination.name] || PORT_COORDINATES[route.destination.name.split(',')[0]];
            if (destCoords && destCoords.lat !== 0 && destCoords.lng !== 0) {
                const key = `${destCoords.lat.toFixed(4)}-${destCoords.lng.toFixed(4)}`;
                const existing = uniquePorts.get(key);
                if (!existing) {
                    uniquePorts.set(key, {
                        coords: destCoords,
                        isActive: isActive,
                        portName: route.destination.name
                    });
                } else if (isActive) {
                    uniquePorts.set(key, { ...existing, isActive: true });
                }
            }
        });
        
        return Array.from(uniquePorts.values()).map((port, index) => {
            const portLabel = port.portName.split(',')[0].replace('Port of ', '').trim();
            
            return (
                <Marker
                    key={`port-${index}-${port.coords.lat}-${port.coords.lng}`}
                    position={port.coords}
                    label={{
                        text: portLabel,
                        color: port.isActive ? '#06b6d4' : '#6b7280',
                        fontWeight: 'bold',
                        fontSize: '12px',
                    }}
                    title={port.portName}
                />
            );
        });
    }, [routes, portCoords, activeRouteId]);

    // Google Maps API Key
    const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

    if (!GOOGLE_MAPS_API_KEY) {
        return (
            <div className="w-full h-96 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-600 dark:text-gray-400 mb-2">Google Maps API Key Required</p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                        Add VITE_GOOGLE_MAPS_API_KEY to your .env file
                    </p>
                </div>
            </div>
        );
    }

    if (isLoadingCoords) {
        return (
            <div className="w-full h-96 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                <div className="text-center">
                    <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading map...</p>
                </div>
            </div>
        );
    }

    return (
        <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY}>
            <GoogleMap
                mapContainerStyle={mapContainerStyle}
                center={defaultCenter}
                zoom={defaultOptions.zoom}
                options={defaultOptions}
            >
                {/* Draw routes */}
                {routePaths.map((path, index) => {
                    if (path.length < 2) return null;
                    
                    const route = routes[index];
                    return (
                        <Polyline
                            key={route.id}
                            path={path}
                            options={{
                                strokeColor: getRouteColor(route.id),
                                strokeOpacity: getRouteOpacity(route.id),
                                strokeWeight: getRouteWeight(route.id),
                                geodesic: true,
                            }}
                        />
                    );
                })}

                {/* Mark all ports - using pre-computed portMarkers */}
                {portMarkers}

                {/* Mark risk events */}
                {riskMarkers.map(marker => (
                    <Marker
                        key={marker.id}
                        position={marker.position}
                        title={marker.title}
                    />
                ))}
            </GoogleMap>
        </LoadScript>
    );
};

export default RouteMap;
