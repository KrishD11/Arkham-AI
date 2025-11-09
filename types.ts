export interface Port {
    id: string;
    name: string;
}

export interface Route {
    id: string;
    name: string;
    origin: Port;
    destination: Port;
    stops?: Port[];
    timeDeltaDays: number;
    costDeltaUSD: number;
}

export interface Shipment {
    id: string;
    contents: string;
    origin: Port;
    destination: Port;
    currentRouteId: string;
    eta: number;
}

export interface DisruptionEvent {
    name: string;
    description: string;
}

export interface RiskProfile {
    [routeId: string]: {
        overall: number;
        factors: {
            congestion: number;
            tariffs: number;
            unrest: number;
        };
    };
}

export interface EventLog {
    message: string;
    timestamp: Date;
}

export interface UserConfiguration {
    product: string;
    origin: string;
    destination: string;
}