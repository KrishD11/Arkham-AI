import type { Port, Route, Shipment, DisruptionEvent } from './types';

export const PORTS: { [key: string]: Port } = {
    taiwan: { id: 'TWTPE', name: 'Port of Taipei, Taiwan' },
    vietnam: { id: 'VNSGN', name: 'Port of Ho Chi Minh City, Vietnam' },
    japan: { id: 'JPTYO', name: 'Port of Tokyo, Japan' },
    los_angeles: { id: 'USLAX', name: 'Port of Los Angeles, USA' },
};

export const PRIMARY_ROUTE: Route = {
    id: 'TW-LA-DIRECT',
    name: 'Primary: Taiwan -> Los Angeles',
    origin: PORTS.taiwan,
    destination: PORTS.los_angeles,
    timeDeltaDays: 0,
    costDeltaUSD: 0,
};

export const ALTERNATIVE_ROUTES: Route[] = [
    {
        id: 'TW-VN-LA',
        name: 'Alternative: Taiwan -> Vietnam -> Los Angeles',
        origin: PORTS.taiwan,
        destination: PORTS.los_angeles,
        stops: [PORTS.vietnam],
        timeDeltaDays: 1,
        costDeltaUSD: 15000,
    },
    {
        id: 'TW-JP-LA',
        name: 'Alternative: Taiwan -> Japan -> Los Angeles',
        origin: PORTS.taiwan,
        destination: PORTS.los_angeles,
        stops: [PORTS.japan],
        timeDeltaDays: 2,
        costDeltaUSD: 25000,
    }
];

export const INITIAL_SHIPMENT: Shipment = {
    id: 'ARK-SC-123',
    contents: '100x Semiconductor Containers',
    origin: PORTS.taiwan,
    destination: PORTS.los_angeles,
    currentRouteId: PRIMARY_ROUTE.id,
    eta: 14, // days
};

export const DISRUPTION_EVENT: DisruptionEvent = {
    name: 'New Tariffs on Taiwan Exports',
    description: 'A new trade tariff has been announced that will impact all exports from Taiwan, potentially causing significant delays and cost increases.',
};