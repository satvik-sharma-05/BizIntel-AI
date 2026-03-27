"""
Intelligent Chat Service - OPTIMIZED
Combines RAG (documents), multi-agent system, and general AI knowledge
Fast and efficient with smart caching
"""
from typing import Dict, Any, List, Optional
from ..rag.rag_pipeline import rag_pipeline
from ..agents.orchestrator import orchestrator
from ..agents.decision_agent import decision_agent
from ..services.llm_service import call_openrouter
from ..database.mongodb import collections
import asyncio

class IntelligentChat:
    """
    Smart chat system that:
    1. Checks for relevant documents (RAG) - FAST
    2. Uses specialized agents ONLY when needed - OPTIONAL
    3. Combines everything with AI knowledge - ALWAYS
    """
    
    def __init__(self):
        self._business_cache = {}  # Cache business context
    
    async def process_message(
        self,
        message: str,
        business_id: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None,
        mode: str = "full_intelligence"
    ) -> Dict[str, Any]:
        """
        Process a chat message intelligently and FAST
        
        Modes:
        - knowledge_base_only: RAG only, strict document answers
        - ai_knowledge_base: RAG + AI analysis
        - ai_only: LLM only, no documents or agents
        - business_data_only: Agents only, no documents
        - full_intelligence: Everything combined
        
        Returns:
            {
                "response": str,
                "sources": {...},
                "citations": [...],
                "agents_used": [...]
            }
        """
        
        # Route based on mode
        if mode == "knowledge_base_only":
            return await self._knowledge_base_only(message, business_id, business, conversation_history)
        
        elif mode == "ai_knowledge_base":
            return await self._ai_knowledge_base(message, business_id, business, conversation_history)
        
        elif mode == "ai_only":
            return await self._ai_only(message, business, conversation_history)
        
        elif mode == "business_data_only":
            return await self._business_data_only(message, business, conversation_history)
        
        else:  # full_intelligence (default)
            return await self._full_intelligence(message, business_id, business, conversation_history)
    
    async def _get_document_context(
        self,
        message: str,
        business_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get relevant document context if available - FAST"""
        try:
            # Quick check: Do documents exist?
            doc_count = await collections.documents().count_documents({
                "business_id": business_id
            })
            
            if doc_count == 0:
                return None
            
            # Hybrid search: FAISS + BM25 + Neo4j + MongoDB
            rag_result = await rag_pipeline.query(
                question=message,
                business_id=business_id,
                mode="hybrid",
                top_k=3  # Reduced from 5 for speed
            )
            
            if rag_result.get("has_documents") and rag_result.get("citations"):
                return {
                    "chunks": rag_result.get("citations", []),
                    "context": self._build_document_summary(rag_result.get("citations", []))
                }
            
            return None
            
        except Exception as e:
            print(f"Document context error: {str(e)}")
            return None
    
    async def _get_agent_context(
        self,
        message: str,
        business: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get agent analysis ONLY if needed - Can be slow"""
        try:
            # Double check if we really need agents
            if not self._needs_agents(message):
                return None
            
            print(f"🤖 Running agents for: {message[:50]}...")
            
            # Build context for agents
            context = {
                "business_id": str(business.get("_id")),
                "business_name": business.get("name"),
                "industry": business.get("industry"),
                "city": business.get("city"),
                "state": business.get("state"),
                "investment": business.get("investment"),
                "query": message
            }
            
            # Run orchestrator with timeout
            try:
                orch_result = await asyncio.wait_for(
                    orchestrator.run(context),
                    timeout=10.0  # 10 second timeout
                )
            except asyncio.TimeoutError:
                print("⚠️ Agent timeout - skipping")
                return None
            
            if not orch_result.get("success"):
                return None
            
            orch_data = orch_result.get("data", {})
            agents_used = orch_data.get("agents_executed", [])
            
            # Build enhanced context for decision agent
            decision_context = {
                **context,
                "data": orch_data.get("data", {}),
                "market_analysis": orch_data.get("market_analysis", {}),
                "location_analysis": orch_data.get("location_analysis", {})
            }
            
            # Get decision from decision agent (with timeout)
            try:
                decision_result = await asyncio.wait_for(
                    decision_agent.run(decision_context),
                    timeout=5.0  # 5 second timeout
                )
            except asyncio.TimeoutError:
                print("⚠️ Decision agent timeout - using orchestrator data")
                return {
                    "agents_used": agents_used,
                    "analysis": orch_data,
                    "summary": self._build_agent_summary(orch_data)
                }
            
            if decision_result.get("success"):
                return {
                    "agents_used": agents_used + ["decision_agent"],
                    "analysis": decision_result.get("data", {}),
                    "summary": self._build_agent_summary(decision_result.get("data", {}))
                }
            
            return None
            
        except Exception as e:
            print(f"Agent context error: {str(e)}")
            return None
    
    async def _generate_combined_response(
        self,
        message: str,
        business: Dict[str, Any],
        document_context: Optional[Dict[str, Any]],
        agent_context: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate response combining all sources"""
        
        # Build comprehensive system prompt
        system_prompt = self._build_system_prompt(
            business=business,
            has_documents=document_context is not None,
            has_agents=agent_context is not None
        )
        
        # Build user prompt with all context
        user_prompt = self._build_user_prompt(
            message=message,
            document_context=document_context,
            agent_context=agent_context
        )
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 5 messages)
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        # Add current message
        messages.append({"role": "user", "content": user_prompt})
        
        # Generate response
        ai_response = call_openrouter(messages, max_tokens=2000)
        
        # Build result
        result = {
            "response": ai_response,
            "sources": {
                "documents": document_context is not None,
                "agents": agent_context is not None,
                "ai_knowledge": True
            },
            "citations": document_context.get("chunks", []) if document_context else [],
            "agents_used": agent_context.get("agents_used", []) if agent_context else [],
            "rag_used": document_context is not None
        }
        
        return result
    
    def _build_system_prompt(
        self,
        business: Dict[str, Any],
        has_documents: bool,
        has_agents: bool
    ) -> str:
        """Build comprehensive system prompt"""
        
        business_name = business.get('name') or business.get('business_name', 'the business')
        industry = business.get('industry', 'Not specified')
        city = business.get('city', 'Not specified')
        state = business.get('state', 'Not specified')
        investment = business.get('investment') or business.get('initial_investment', 0)
        description = business.get('description', '')
        
        prompt = f"""You are an AI business intelligence assistant for BizIntel AI.

## CRITICAL: You are analyzing THIS specific business:

**Business Name:** {business_name}
**Industry:** {industry}
**Location:** {city}, {state}
**Initial Investment:** ₹{investment:,.0f}
"""
        
        if description:
            prompt += f"**Description:** {description}\n"
        
        prompt += f"""
**IMPORTANT:** When the user asks "what is my business?" or similar questions, you MUST tell them about THIS business ({business_name} in {city}, {state}, {industry} industry). Do NOT say you don't know - you have this information!

## Your Capabilities

You have access to multiple sources of information:
"""
        
        if has_documents:
            prompt += """
1. **📄 Document Knowledge**: Uploaded business documents (plans, reports, etc.)
   - Use these for specific facts, figures, and documented strategies
   - Always cite documents when using their information
"""
        
        if has_agents:
            prompt += """
2. **🤖 Agent Analysis**: Real-time data from specialized agents
   - Market analysis, location intelligence, economic data
   - Use for current market conditions and data-driven insights
"""
        
        prompt += """
3. **🧠 AI Knowledge**: Your general business expertise
   - Industry best practices, strategies, recommendations
   - Use for analysis, interpretation, and expert advice

## Response Guidelines

**IMPORTANT**: You should combine ALL available sources intelligently:

- If documents contain relevant info → Reference them with citations
- If agents provide data → Include their insights
- Always add your expert analysis and recommendations
- Use markdown formatting for beautiful, structured responses

**Structure your response:**

## [Main Answer]
[Comprehensive answer using all sources]

## Document Insights (if applicable)
[What the documents say - with citations]

## Market Intelligence (if applicable)
[What the agents found - current data]

## Expert Analysis
[Your AI analysis and recommendations]

## Key Takeaways
- [Actionable point 1]
- [Actionable point 2]
- [Actionable point 3]

**Formatting:**
- Use **bold** for emphasis
- Use bullet points and tables
- Use headings (##, ###)
- Be specific and actionable
- Use Indian market context and ₹ currency
"""
        
        return prompt
    
    def _build_user_prompt(
        self,
        message: str,
        document_context: Optional[Dict[str, Any]],
        agent_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt with all context"""
        
        prompt = f"**User Question:** {message}\n\n"
        
        # Add agent context first (more important for business questions)
        if agent_context:
            prompt += "**🤖 Real-Time Business Intelligence:**\n"
            prompt += agent_context.get("summary", "")
            prompt += "\n\n"
        
        # Then document context
        if document_context:
            prompt += "**📄 Relevant Documents:**\n"
            prompt += document_context.get("context", "")
            prompt += "\n\n"
        
        prompt += """**Instructions:**
Provide a comprehensive answer that:
1. **ALWAYS starts with the business context** (name, industry, location) when relevant
2. Addresses the user's question directly
3. Incorporates agent analysis (if available) - this includes market data, location intelligence, etc.
4. Includes document insights (if available)
5. Adds your expert recommendations
6. Is well-formatted with markdown

**CRITICAL:** If the user asks about "my business" or similar, you MUST provide the business details from the system context. Never say you don't know what their business is!

Remember: You have access to:
- Business profile (name, industry, location, investment)
- Real-time market data (from agents)
- Uploaded documents (from RAG)
- Your business expertise
"""
        
        return prompt
    
    def _build_document_summary(self, citations: List[Dict[str, Any]]) -> str:
        """Build summary of document context"""
        summary = ""
        for i, citation in enumerate(citations, 1):
            summary += f"\n[Document {i}] {citation['filename']} (Page {citation['page_number']})\n"
            summary += f"Relevance: {citation.get('similarity', 0) * 100:.0f}%\n"
        return summary
    
    def _build_agent_summary(self, analysis: Dict[str, Any]) -> str:
        """Build summary of agent analysis"""
        summary = "\n**Agent Insights:**\n"
        
        # Check for markdown analysis from agents (new format)
        market_analysis = analysis.get("market_analysis", {})
        location_analysis = analysis.get("location_analysis", {})
        
        # Use markdown analysis if available
        if isinstance(market_analysis, dict) and "markdown_analysis" in market_analysis:
            summary += "\n" + market_analysis["markdown_analysis"] + "\n"
        elif isinstance(market_analysis, dict):
            # Fallback to old format
            if "demand_score" in market_analysis:
                summary += f"- Demand Score: {market_analysis.get('demand_score', 'N/A')}/100\n"
            if "opportunity" in market_analysis:
                summary += f"- Market Opportunity: {market_analysis.get('opportunity', 'N/A')}\n"
            if "competition" in market_analysis:
                summary += f"- Competition Level: {market_analysis.get('competition', 'N/A')}\n"
            if "profit_potential" in market_analysis:
                summary += f"- Profit Potential: {market_analysis.get('profit_potential', 'N/A')}\n"
        
        if isinstance(location_analysis, dict) and "markdown_analysis" in location_analysis:
            summary += "\n" + location_analysis["markdown_analysis"] + "\n"
        elif isinstance(location_analysis, dict) and "recommendations" in location_analysis:
            # Fallback to old format
            recommendations = location_analysis.get("recommendations", [])
            if recommendations:
                summary += f"\n**Top Expansion Cities:**\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    summary += f"{i}. {rec.get('city', 'N/A')}, {rec.get('state', 'N/A')} - Score: {rec.get('overall_score', 'N/A')}/100\n"
        
        # Legacy format support
        if "market_viability" in analysis:
            summary += f"- Market Viability Score: {analysis.get('market_viability', 'N/A')}/10\n"
        
        if "market_size" in analysis:
            summary += f"- Market Size: {analysis.get('market_size', 'N/A')}\n"
        
        if "competition_level" in analysis:
            summary += f"- Competition Level: {analysis.get('competition_level', 'N/A')}\n"
        
        if "location_score" in analysis:
            summary += f"- Location Score: {analysis.get('location_score', 'N/A')}/10\n"
        
        if "revenue_forecast" in analysis:
            summary += f"- Revenue Forecast: {analysis.get('revenue_forecast', 'N/A')}\n"
        
        if "recommendation" in analysis:
            summary += f"- Overall Recommendation: {analysis.get('recommendation', 'N/A')}\n"
        
        if "confidence_score" in analysis:
            summary += f"- Confidence Score: {analysis.get('confidence_score', 'N/A')}%\n"
        
        # Add full analysis if available
        if "full_analysis" in analysis:
            summary += f"\n**Detailed Analysis:**\n{analysis.get('full_analysis', '')[:500]}...\n"
        
        return summary
    
    def _needs_agents(self, message: str) -> bool:
        """
        Determine if message REALLY needs agent analysis
        Be selective to keep responses fast!
        """
        message_lower = message.lower()
        
        # Simple questions that DON'T need agents
        simple_patterns = [
            "hi", "hello", "hey", "thanks", "thank you", "ok", "okay",
            "yes", "no", "sure", "great", "good", "bye", "goodbye"
        ]
        
        if any(pattern == message_lower.strip() for pattern in simple_patterns):
            return False
        
        # Questions about documents DON'T need agents
        document_patterns = [
            "what does", "what is in", "show me", "find in", "search for",
            "according to", "in the document", "in my document", "pdf says"
        ]
        
        if any(pattern in message_lower for pattern in document_patterns):
            return False
        
        # Only trigger agents for these specific cases
        agent_triggers = [
            # Market analysis
            "market", "competition", "competitor", "industry trend",
            # Location specific
            "expand to", "open in", "location for", "city for", "where should",
            # Data-driven questions
            "forecast", "predict", "projection", "estimate",
            # Strategic questions
            "should i", "is it good", "recommend", "best strategy",
            # Sector analysis
            "sector looking", "industry looking", "market looking",
            # Business overview (only when asking about the business itself)
            "what is my business", "tell me about my business", "business overview"
        ]
        
        return any(trigger in message_lower for trigger in agent_triggers)

    # ============ MODE-SPECIFIC METHODS ============
    
    async def _knowledge_base_only(
        self,
        message: str,
        business_id: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """RAG only - strict document answers"""
        document_context = await self._get_document_context(message, business_id)
        
        if not document_context:
            return {
                "response": "I don't have any documents uploaded for this business yet. Please upload documents to use Knowledge Base mode, or switch to another mode for general assistance.",
                "sources": {"documents": False, "agents": False, "ai_knowledge": False},
                "citations": [],
                "agents_used": [],
                "rag_used": False
            }
        
        # Use RAG pipeline in document-only mode (hybrid search)
        from ..rag.rag_pipeline import rag_pipeline
        rag_result = await rag_pipeline.query(
            question=message,
            business_id=business_id,
            mode="document_only",
            top_k=5
        )
        
        return {
            "response": rag_result.get("answer", "No relevant information found in documents."),
            "sources": {"documents": True, "agents": False, "ai_knowledge": False},
            "citations": rag_result.get("citations", []),
            "agents_used": [],
            "rag_used": True
        }
    
    async def _ai_knowledge_base(
        self,
        message: str,
        business_id: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """RAG + AI analysis"""
        document_context = await self._get_document_context(message, business_id)
        
        response = await self._generate_combined_response(
            message=message,
            business=business,
            document_context=document_context,
            agent_context=None,  # No agents in this mode
            conversation_history=conversation_history
        )
        
        return response
    
    async def _ai_only(
        self,
        message: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """LLM only - no documents or agents"""
        response = await self._generate_combined_response(
            message=message,
            business=business,
            document_context=None,  # No documents
            agent_context=None,  # No agents
            conversation_history=conversation_history
        )
        
        return response
    
    async def _business_data_only(
        self,
        message: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Agents only - no documents"""
        agent_context = await self._get_agent_context(message, business)
        
        if not agent_context:
            # Force agent execution for this mode
            print(f"🤖 Forcing agent execution for business_data_only mode")
            agent_context = await self._get_agent_context(message, business)
        
        response = await self._generate_combined_response(
            message=message,
            business=business,
            document_context=None,  # No documents
            agent_context=agent_context,
            conversation_history=conversation_history
        )
        
        return response
    
    async def _full_intelligence(
        self,
        message: str,
        business_id: str,
        business: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Everything combined - original behavior"""
        # Quick check: Does this need agents? (expensive operation)
        needs_agents = self._needs_agents(message)
        
        # Run document search and agent analysis in parallel (if needed)
        if needs_agents:
            # Parallel execution for speed
            document_task = self._get_document_context(message, business_id)
            agent_task = self._get_agent_context(message, business)
            
            document_context, agent_context = await asyncio.gather(
                document_task,
                agent_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(document_context, Exception):
                print(f"Document context error: {document_context}")
                document_context = None
            if isinstance(agent_context, Exception):
                print(f"Agent context error: {agent_context}")
                agent_context = None
        else:
            # Only check documents (fast)
            document_context = await self._get_document_context(message, business_id)
            agent_context = None
        
        # Generate response
        response = await self._generate_combined_response(
            message=message,
            business=business,
            document_context=document_context,
            agent_context=agent_context,
            conversation_history=conversation_history
        )
        
        return response

# Global instance
intelligent_chat = IntelligentChat()
