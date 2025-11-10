import type { Port, Route, Shipment, DisruptionEvent } from './types';

// Major world ports commonly used for shipments (based on public shipping data)
export const PORTS: { [key: string]: Port } = {
    // Asia-Pacific
    taiwan: { id: 'TWTPE', name: 'Port of Taipei, Taiwan' },
    shanghai: { id: 'CNSHA', name: 'Port of Shanghai, China' },
    shenzhen: { id: 'CNSZN', name: 'Port of Shenzhen, China' },
    singapore: { id: 'SGSIN', name: 'Port of Singapore, Singapore' },
    hong_kong: { id: 'HKHKG', name: 'Port of Hong Kong, China' },
    busan: { id: 'KRBUS', name: 'Port of Busan, South Korea' },
    japan: { id: 'JPTYO', name: 'Port of Tokyo, Japan' },
    yokohama: { id: 'JPYOK', name: 'Port of Yokohama, Japan' },
    vietnam: { id: 'VNSGN', name: 'Port of Ho Chi Minh City, Vietnam' },
    bangkok: { id: 'THBKK', name: 'Port of Bangkok, Thailand' },
    jakarta: { id: 'IDJKT', name: 'Port of Jakarta, Indonesia' },
    manila: { id: 'PHMNL', name: 'Port of Manila, Philippines' },
    mumbai: { id: 'INMUM', name: 'Port of Mumbai, India' },
    chennai: { id: 'INMAA', name: 'Port of Chennai, India' },
    
    // Middle East
    dubai: { id: 'AEDXB', name: 'Port of Dubai, UAE' },
    jeddah: { id: 'SAJED', name: 'Port of Jeddah, Saudi Arabia' },
    
    // Europe
    rotterdam: { id: 'NLRTM', name: 'Port of Rotterdam, Netherlands' },
    hamburg: { id: 'DEHAM', name: 'Port of Hamburg, Germany' },
    antwerp: { id: 'BEANR', name: 'Port of Antwerp, Belgium' },
    london: { id: 'GBLON', name: 'Port of London, UK' },
    felixstowe: { id: 'GBFEL', name: 'Port of Felixstowe, UK' },
    le_havre: { id: 'FRLEH', name: 'Port of Le Havre, France' },
    genoa: { id: 'ITGOA', name: 'Port of Genoa, Italy' },
    barcelona: { id: 'ESBCN', name: 'Port of Barcelona, Spain' },
    piraeus: { id: 'GRPIR', name: 'Port of Piraeus, Greece' },
    
    // North America
    los_angeles: { id: 'USLAX', name: 'Port of Los Angeles, USA' },
    long_beach: { id: 'USLGB', name: 'Port of Long Beach, USA' },
    new_york: { id: 'USNYC', name: 'Port of New York/Newark, USA' },
    savannah: { id: 'USSAV', name: 'Port of Savannah, USA' },
    charleston: { id: 'USCHS', name: 'Port of Charleston, USA' },
    houston: { id: 'USHOU', name: 'Port of Houston, USA' },
    vancouver: { id: 'CAVAN', name: 'Port of Vancouver, Canada' },
    
    // South America
    santos: { id: 'BRSSZ', name: 'Port of Santos, Brazil' },
    buenos_aires: { id: 'ARBUE', name: 'Port of Buenos Aires, Argentina' },
    callao: { id: 'PECLL', name: 'Port of Callao, Peru' },
    
    // Africa
    durban: { id: 'ZADUR', name: 'Port of Durban, South Africa' },
    cape_town: { id: 'ZACPT', name: 'Port of Cape Town, South Africa' },
    lagos: { id: 'NGLOS', name: 'Port of Lagos, Nigeria' },
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
    },
    {
        id: 'TW-SG-LA',
        name: 'Alternative: Taiwan -> Singapore -> Los Angeles',
        origin: PORTS.taiwan,
        destination: PORTS.los_angeles,
        stops: [PORTS.singapore],
        timeDeltaDays: 3,
        costDeltaUSD: 18000,
    },
    {
        id: 'TW-SH-LA',
        name: 'Alternative: Taiwan -> Shanghai -> Los Angeles',
        origin: PORTS.taiwan,
        destination: PORTS.los_angeles,
        stops: [PORTS.shanghai],
        timeDeltaDays: 2,
        costDeltaUSD: 12000,
    },
];

export const INITIAL_SHIPMENT: Shipment = {
    id: 'ARK-SC-123',
    contents: '100x Semiconductor Containers',
    origin: PORTS.taiwan,
    destination: PORTS.los_angeles,
    currentRouteId: PRIMARY_ROUTE.id,
    eta: 14, // days
};

// Dynamic disruption events - varied scenarios
export const DISRUPTION_EVENTS: DisruptionEvent[] = [
    {
        name: 'Port Congestion at Los Angeles',
        description: 'Severe container backlog at Port of Los Angeles causing 5-7 day delays. Labor shortages and increased vessel traffic contributing to congestion.',
    },
    {
        name: 'Trade Route Tensions in South China Sea',
        description: 'Increased military activity and diplomatic tensions affecting shipping lanes through the South China Sea. Vessels reporting longer transit times.',
    },
    {
        name: 'Weather Disruption - Typhoon Warning',
        description: 'Typhoon forecast affecting shipping routes in the Western Pacific. Multiple ports temporarily closed, vessels rerouting to avoid severe weather.',
    },
    {
        name: 'Labor Strike at Major Port',
        description: 'Port workers union strike affecting operations at multiple terminals. Delays expected for all vessels scheduled to dock in the next 48 hours.',
    },
    {
        name: 'Fuel Price Surge',
        description: 'Sudden spike in marine fuel prices affecting shipping costs. Bunker fuel costs increased by 25%, impacting route economics.',
    },
    {
        name: 'Regulatory Changes - New Customs Requirements',
        description: 'New customs documentation requirements announced. Additional processing time expected at destination ports, potential for delays.',
    },
    {
        name: 'Cyber Attack on Port Systems',
        description: 'Cybersecurity incident affecting port management systems. Operations slowed while systems are restored, causing delays.',
    },
    {
        name: 'Bridge Closure - Major Shipping Lane',
        description: 'Critical bridge closure affecting access to major port. Alternative routes required, adding transit time and costs.',
    },
];

// Function to get a random disruption event
export function getRandomDisruptionEvent(): DisruptionEvent {
    return DISRUPTION_EVENTS[Math.floor(Math.random() * DISRUPTION_EVENTS.length)];
}

// Legacy constant for backward compatibility
export const DISRUPTION_EVENT: DisruptionEvent = DISRUPTION_EVENTS[0];