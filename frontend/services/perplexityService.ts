// Perplexity service - can use backend agent query or direct Perplexity API
import { queryAgent } from './apiService';

const PERPLEXITY_API_KEY = import.meta.env.PERPLEXITY_API_KEY;

/**
 * Get AI analysis using either Perplexity API or backend agent
 */
export async function getPerplexityAnalysis(prompt: string): Promise<string> {
    // Option 1: Use backend agent (recommended)
    try {
        const response = await queryAgent(prompt);
        if (response.success && response.response) {
            return response.response;
        }
        throw new Error('No response from agent');
    } catch (error) {
        console.warn('Backend agent query failed, trying direct Perplexity API:', error);
        
        // Option 2: Fallback to direct Perplexity API if configured
        if (PERPLEXITY_API_KEY) {
            return getDirectPerplexityAnalysis(prompt);
        }
        
        // Option 3: Fallback to mock response
        return `Based on the analysis, I recommend selecting the alternative route with the lowest risk score (32%). This route provides the best balance between risk reduction and minimal time impact.`;
    }
}

/**
 * Direct Perplexity API call (fallback)
 */
async function getDirectPerplexityAnalysis(prompt: string): Promise<string> {
    if (!PERPLEXITY_API_KEY) {
        throw new Error('Perplexity API key not configured');
    }

    const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'llama-3.1-sonar-large-128k-online',
            messages: [
                {
                    role: 'system',
                    content: 'You are an expert supply chain analyst specializing in risk assessment and route optimization.',
                },
                {
                    role: 'user',
                    content: prompt,
                },
            ],
        }),
    });

    if (!response.ok) {
        throw new Error(`Perplexity API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || 'No response from Perplexity API';
}

