import React, { useState, useEffect, useRef } from "react";
import {
  MessageSquare,
  Send,
  Plus,
  Trash2,
  FileText,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Copy,
  Check,
  Loader2,
  Scale,
  Sparkles,
  BookOpen,
} from "lucide-react";
import {
  sendChatMessage,
  getChatConversations,
  getChatMessages,
  deleteChatConversation,
} from "../../services/api";

const STARTER_QUESTIONS = [
  "What is the notice period for terminating this agreement?",
  "What are the payment terms and deadlines?",
  "Are there any penalties or late fees specified?",
  "What are my main confidentiality obligations?",
  "Can the other party terminate this agreement without cause?",
  "Is there an automatic renewal clause or renewal trap?",
  "What governing law and jurisdiction apply to this contract?",
];

export default function ChatTab({ documentId, onSelectPage = null }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  // Load conversations list
  useEffect(() => {
    async function loadConversations() {
      if (!documentId) return;
      try {
        setLoadingConversations(true);
        setError(null);
        const data = await getChatConversations(documentId);
        setConversations(data || []);
        if (data && data.length > 0 && !activeConversationId) {
          setActiveConversationId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load conversations", err);
        setError("Unable to load chat history.");
      } finally {
        setLoadingConversations(false);
      }
    }
    loadConversations();
  }, [documentId]);

  // Load messages when active conversation changes
  useEffect(() => {
    async function loadMessages() {
      if (!documentId || !activeConversationId) {
        setMessages([]);
        return;
      }
      try {
        setLoadingMessages(true);
        setError(null);
        const data = await getChatMessages(documentId, activeConversationId);
        setMessages(data || []);
      } catch (err) {
        console.error("Failed to load messages", err);
        setError("Unable to load messages for this conversation.");
      } finally {
        setLoadingMessages(false);
      }
    }
    loadMessages();
  }, [documentId, activeConversationId]);

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setInputMessage("");
    inputRef.current?.focus();
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    try {
      await deleteChatConversation(documentId, convId);
      const remaining = conversations.filter((c) => c.id !== convId);
      setConversations(remaining);
      if (activeConversationId === convId) {
        if (remaining.length > 0) {
          setActiveConversationId(remaining[0].id);
        } else {
          setActiveConversationId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error("Failed to delete conversation", err);
      setError("Could not delete conversation.");
    }
  };

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || sending) return;

    setInputMessage("");
    setError(null);
    setSending(true);

    // Optimistic user message
    const tempUserMsg = {
      id: "temp-" + Date.now(),
      role: "user",
      content: text,
      createdAt: new Date().toISOString(),
      citations: [],
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendChatMessage(documentId, {
        conversationId: activeConversationId,
        message: text,
      });

      // Update active conversation id if this was a new thread
      if (!activeConversationId && response.conversationId) {
        setActiveConversationId(response.conversationId);
        // Refresh conversations list
        const updatedList = await getChatConversations(documentId);
        setConversations(updatedList || []);
      }

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        tempUserMsg,
        response,
      ]);
    } catch (err) {
      console.error("Failed to send message", err);
      setError(
        err.response?.data?.message ||
          "Failed to get a response. Please verify the AI engine is running."
      );
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 overflow-hidden shadow-sm flex flex-col md:flex-row min-h-[640px] max-h-[780px]">
      {/* Sidebar: Conversation Threads */}
      <div className="w-full md:w-64 lg:w-72 border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-800 flex flex-col bg-slate-50/60 dark:bg-slate-900/60">
        <div className="p-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
            <MessageSquare className="w-4 h-4 text-blue-600" />
            Conversations
          </span>
          <button
            type="button"
            onClick={handleNewConversation}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> New
          </button>
        </div>

        {/* Thread List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loadingConversations ? (
            <div className="py-8 text-center text-xs text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin mx-auto mb-1 text-blue-600" />
              Loading history...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-500">
              No conversations yet. Start asking questions about this document.
            </div>
          ) : (
            conversations.map((c) => {
              const isActive = c.id === activeConversationId;
              return (
                <div
                  key={c.id}
                  onClick={() => setActiveConversationId(c.id)}
                  className={`group px-2.5 py-2 rounded-md cursor-pointer text-xs flex items-center justify-between transition-colors ${
                    isActive
                      ? "bg-blue-50 dark:bg-blue-950/40 text-blue-900 dark:text-blue-200 border border-blue-200 dark:border-blue-900"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent"
                  }`}
                >
                  <div className="truncate flex-1 mr-2">
                    <p className="font-medium truncate">{c.title || "Inquiry"}</p>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
                      {c.messageCount || 0} messages
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    title="Delete thread"
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 transition-opacity"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Main Chat Panel */}
      <div className="flex-1 flex flex-col bg-white dark:bg-slate-900">
        {/* Top Header */}
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs bg-slate-50/40 dark:bg-slate-900/40">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              Document Grounded Chat
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-mono">
              FTS retrieval + citations
            </span>
          </div>
          <span className="text-[11px] text-slate-500">
            Answers strictly derived from contract text
          </span>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {loadingMessages ? (
            <div className="py-20 text-center text-xs text-slate-400">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
              Loading conversation messages...
            </div>
          ) : messages.length === 0 ? (
            /* Empty State & Starter Questions */
            <div className="py-8 max-w-xl mx-auto space-y-6 text-center">
              <div className="space-y-1">
                <div className="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto mb-2">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Ask Anything About This Contract
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Every response is grounded strictly in the document text with structured page citations.
                </p>
              </div>

              {/* Starter Questions Grid */}
              <div className="space-y-2 text-left">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 px-1">
                  Suggested Starter Questions
                </p>
                <div className="grid grid-cols-1 gap-1.5">
                  {STARTER_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSendMessage(q)}
                      disabled={sending}
                      className="w-full text-left p-2.5 rounded-md border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-600 bg-slate-50/50 dark:bg-slate-800/40 hover:bg-blue-50/50 dark:hover:bg-blue-950/20 text-xs text-slate-700 dark:text-slate-300 transition-colors flex items-center justify-between group"
                    >
                      <span>{q}</span>
                      <Send className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 transition-colors opacity-0 group-hover:opacity-100 flex-shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Message Thread */
            messages.map((msg, index) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id || index}
                  className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3.5 text-xs leading-relaxed space-y-2.5 ${
                      isUser
                        ? "bg-slate-900 text-white dark:bg-blue-700 dark:text-white rounded-br-none"
                        : "bg-slate-50 dark:bg-slate-800/80 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700/80 rounded-bl-none shadow-sm"
                    }`}
                  >
                    {/* Header for assistant message */}
                    {!isUser && (
                      <div className="flex items-center justify-between gap-3 pb-1 border-b border-slate-200/60 dark:border-slate-700/60 text-[11px] text-slate-500">
                        <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                          <Scale className="w-3.5 h-3.5 text-blue-600" />
                          LexiLegal Assistant
                        </span>
                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => handleCopy(msg.id, msg.content)}
                            title="Copy answer"
                            className="p-1 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                          >
                            {copiedId === msg.id ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Message Body */}
                    <div className="whitespace-pre-wrap select-text font-normal">
                      {msg.content}
                    </div>

                    {/* Grounding & Citations section */}
                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div className="pt-2 border-t border-slate-200/60 dark:border-slate-700/60 space-y-1.5">
                        <div className="flex items-center gap-1.5 text-[10px] uppercase font-semibold text-slate-500">
                          <BookOpen className="w-3 h-3 text-blue-600" />
                          <span>Sources & Evidence ({msg.citations.length})</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.citations.map((cit, cIdx) => (
                            <button
                              key={cIdx}
                              type="button"
                              onClick={() => onSelectPage && onSelectPage(cit.page)}
                              title={
                                cit.quote
                                  ? `"${cit.quote}" (Click to view page)`
                                  : "Click to view page"
                              }
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/50 text-blue-800 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"
                            >
                              <span>Page {cit.page}</span>
                              {cit.sectionRef && (
                                <span className="opacity-75">({cit.sectionRef})</span>
                              )}
                              {cit.quoteVerified ? (
                                <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                              ) : (
                                <AlertTriangle className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Unaddressed flag */}
                    {!isUser && msg.addressedInDocument === false && (
                      <div className="text-[10px] text-slate-500 flex items-center gap-1 pt-1">
                        <HelpCircle className="w-3 h-3 text-slate-400" />
                        <span>Not found in retrieved document excerpts</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}

          {/* Typing Indicator */}
          {sending && (
            <div className="flex items-start">
              <div className="max-w-[85%] rounded-lg rounded-bl-none p-3.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs text-slate-500 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span>Searching document excerpts and evaluating citations...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Toolbar */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              rows={2}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={sending}
              placeholder="Ask a question about this contract (e.g. 'What is the notice period?')... [Press Enter to send]"
              className="flex-1 resize-none rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
            <button
              type="button"
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || sending}
              className="inline-flex items-center gap-1 px-4 py-2.5 rounded-md bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-xs font-medium transition-colors h-[42px]"
            >
              <Send className="w-3.5 h-3.5" /> Send
            </button>
          </div>
          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400 px-1">
            <span>Enter to send &bull; Shift + Enter for new line</span>
            <span>{inputMessage.length}/2000</span>
          </div>
        </div>
      </div>
    </div>
  );
}
