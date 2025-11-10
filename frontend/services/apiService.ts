// API service for connecting to Arkham AI backend
const API_URL = import.meta.env.VITE_API_URL || 'https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app';

interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    [key: string]: any;
}

// Helper function for API calls
async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_URL}${endpoint}`;
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

// Health & Info
export const getHealth = () => apiCall('/');
export const getApiHealth = () => apiCall('/api/health');
export const getAgentInfo = () => apiCall('/api/agent/info');

// Agent
export const queryAgent = (message: string, userId: string | null = null) =>
    apiCall('/api/agent/query', {
        method: 'POST',
        body: JSON.stringify({ message, user_id: userId }),
    });

// Data Ingestion
export const getTradeNews = (region: string | null = null, limit: number = 50) => {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    params.append('limit', limit.toString());
    return apiCall(`/api/data/trade-news?${params}`);
};

export const getPoliticalData = (region: string | null = null) => {
    const params = region ? `?region=${region}` : '';
    return apiCall(`/api/data/political${params}`);
};

export const getPortData = (portCode: string | null = null) => {
    const params = portCode ? `?port_code=${portCode}` : '';
    return apiCall(`/api/data/ports${params}`);
};

export const getAllRiskData = (region: string | null = null, portCode: string | null = null) => {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    if (portCode) params.append('port_code', portCode);
    const query = params.toString() ? `?${params}` : '';
    return apiCall(`/api/data/all${query}`);
};

export const getRouteRiskData = (origin: string, destination: string, routeRegions: string[] = []) =>
    apiCall('/api/data/route', {
        method: 'POST',
        body: JSON.stringify({ origin, destination, route_regions: routeRegions }),
    });

// Risk Assessment
export const assessRoute = (
    origin: string,
    destination: string,
    routeRegions: string[] = [],
    routeId: string | null = null
) =>
    apiCall('/api/routes/assess', {
        method: 'POST',
        body: JSON.stringify({
            origin,
            destination,
            route_regions: routeRegions,
            route_id: routeId,
        }),
    });

export const getRouteRisk = (routeId: string) => apiCall(`/api/routes/${routeId}/risk`);

export const compareRoutes = (routes: Array<{ origin: string; destination: string; route_regions?: string[] }>) =>
    apiCall('/api/routes/compare', {
        method: 'POST',
        body: JSON.stringify({ routes }),
    });

// Predictive Scoring
export const predictRouteRisk = (
    origin: string,
    destination: string,
    routeRegions: string[] = [],
    routeId: string | null = null,
    daysAhead: number[] = [3, 5, 7]
) =>
    apiCall('/api/routes/predict', {
        method: 'POST',
        body: JSON.stringify({
            origin,
            destination,
            route_regions: routeRegions,
            route_id: routeId,
            days_ahead: daysAhead,
        }),
    });

export const getRoutePredictions = (routeId: string) => apiCall(`/api/routes/${routeId}/predict`);

// Route Optimization
export const optimizeRoute = (
    origin: string,
    destination: string,
    priority: 'risk' | 'cost' | 'time' | 'balanced' = 'balanced',
    customWeights: { risk?: number; cost?: number; time?: number } | null = null,
    includePredictions: boolean = true,
    maxAlternatives: number = 5
) =>
    apiCall('/api/routes/optimize', {
        method: 'POST',
        body: JSON.stringify({
            origin,
            destination,
            priority,
            custom_weights: customWeights,
            include_predictions: includePredictions,
            max_alternatives: maxAlternatives,
        }),
    });

export const getRoutes = () => apiCall('/api/routes');

// Execution
export const monitorAndExecute = (
    shipmentId: string,
    origin: string,
    destination: string,
    routeRegions: string[] = [],
    executionMode: 'automatic' | 'manual' | 'semi_automatic' = 'semi_automatic'
) =>
    apiCall('/api/execution/monitor', {
        method: 'POST',
        body: JSON.stringify({
            shipment_id: shipmentId,
            origin,
            destination,
            route_regions: routeRegions,
            execution_mode: executionMode,
        }),
    });

export const executeReroute = (
    shipmentId: string,
    newRouteId: string,
    origin: string,
    destination: string,
    routeRegions: string[] = [],
    reason: string = 'Manual reroute'
) =>
    apiCall('/api/execution/execute', {
        method: 'POST',
        body: JSON.stringify({
            shipment_id: shipmentId,
            new_route_id: newRouteId,
            origin,
            destination,
            route_regions: routeRegions,
            reason,
        }),
    });

// Logging
export const getLogs = (
    category: string | null = null,
    level: string | null = null,
    shipmentId: string | null = null,
    routeId: string | null = null,
    limit: number = 100
) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    if (shipmentId) params.append('shipment_id', shipmentId);
    if (routeId) params.append('route_id', routeId);
    params.append('limit', limit.toString());
    return apiCall(`/api/logs?${params}`);
};

export const exportLogs = (filters: Record<string, any> = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            params.append(key, value.toString());
        }
    });
    const query = params.toString() ? `?${params}` : '';
    return apiCall(`/api/logs/export${query}`);
};

// Database (MongoDB)
export const getDbHealth = () => apiCall('/api/db/health');

export const getDbRiskData = (
    category: string | null = null,
    location: string | null = null,
    source: string | null = null,
    limit: number = 100,
    daysBack: number | null = null
) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (location) params.append('location', location);
    if (source) params.append('source', source);
    params.append('limit', limit.toString());
    if (daysBack) params.append('days_back', daysBack.toString());
    return apiCall(`/api/db/risk-data?${params}`);
};

export const getDbStats = () => apiCall('/api/db/stats');

