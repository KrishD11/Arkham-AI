// Vertex AI service for frontend AI queries - Uses backend Arkham AI agent
const BACKEND_API_URL = import.meta.env.VITE_API_URL || 'https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app';

interface VertexAIResponse {
    success: boolean;
    response?: string;
    error?: string;
    agent?: string;
}

/**
 * Query Arkham AI agent through backend endpoint
 * This uses the deployed backend agent at Cloud Run
 */
export async function queryVertexAI(prompt: string): Promise<string> {
    try {
        console.log('Querying Arkham AI agent at:', `${BACKEND_API_URL}/api/agent/query`);
        
        const response = await fetch(`${BACKEND_API_URL}/api/agent/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: prompt,
                user_id: 'frontend-user'
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();
        
        console.log('AI Agent response:', { success: data.success, agent: data.agent });
        
        if (data.success && data.response) {
            return data.response;
        } else {
            throw new Error(data.error || 'No response from AI agent');
        }
    } catch (error) {
        console.error('Error querying Arkham AI agent:', error);
        throw error;
    }
}

/**
 * Get AI recommendation for route optimization using Arkham AI agent
 */
export async function getAIRouteRecommendation(
    originalRoute: { origin: string; destination: string; risk: number },
    alternatives: Array<{ routeId: string; origin: string; destination: string; waypoints: string[]; risk: number; cost: number; time: number }>
): Promise<string> {
    const prompt = `Analyze these shipping routes and provide a recommendation:

Original Route: ${originalRoute.origin} -> ${originalRoute.destination}
- Risk Score: ${(originalRoute.risk * 100).toFixed(0)}%

Alternative Routes:
${alternatives.map((alt, idx) => 
    `${idx + 1}. ${alt.origin} -> ${alt.destination} via ${alt.waypoints.join(', ') || 'direct'}
   - Risk Score: ${(alt.risk * 100).toFixed(0)}%
   - Cost: $${alt.cost.toLocaleString()}
   - Time: ${alt.time} days`
).join('\n')}

Based on the risk assessment, cost, and time analysis, should we reroute? Provide a clear, concise recommendation (2-3 sentences) explaining:
1. Whether to reroute or stay on current route
2. Key reasons (risk reduction, cost/time tradeoffs)
3. Any important considerations

Be specific about the risk factors and why the alternative is better or worse.`;

    return await queryVertexAI(prompt);
}

/**
 * Get agent information from backend
 */
export async function getAgentInfo(): Promise<any> {
    try {
        const response = await fetch(`${BACKEND_API_URL}/api/agent/info`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching agent info:', error);
        throw error;
    }
}

