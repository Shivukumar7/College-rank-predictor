"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Sparkles, User, HelpCircle } from "lucide-react";
import { askChatbot, ChatContext } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface Message {
  sender: "user" | "bot";
  text: string;
}

interface AdmissionsChatbotProps {
  context?: ChatContext;
}

const DEFAULT_SUGGESTIONS = [
  "What documents do I need?",
  "NIT vs IIIT?",
  "Tell me about JoSAA counseling",
  "How to get Computer Science?",
];

export default function AdmissionsChatbot({ context }: AdmissionsChatbotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: "Hello! I am your AI Admissions Counselor. Ask me anything about JoSAA, NEET, KCET, or college admission strategies.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const suggestions = context?.rank
    ? ["What are my chances?", ...DEFAULT_SUGGESTIONS.slice(0, 3)]
    : DEFAULT_SUGGESTIONS;

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;
    
    setMessages((prev) => [...prev, { sender: "user", text: textToSend }]);
    setInputValue("");
    setLoading(true);

    try {
      const data = await askChatbot(textToSend, context);
      setMessages((prev) => [...prev, { sender: "bot", text: data.reply }]);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Oops, I encountered an issue. Please try again shortly!";
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: errMsg },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 print:hidden">
      {/* Floating Bubble */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            key="chat-bubble"
            initial={{ scale: 0, rotate: -45 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 45 }}
            onClick={() => setIsOpen(true)}
            className="flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-tr from-accent-500 to-info-500 text-white shadow-2xl hover:scale-110 active:scale-95 transition-transform cursor-pointer"
          >
            <MessageSquare className="w-6 h-6" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="chat-window"
            initial={{ opacity: 0, y: 100, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.8 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="w-[360px] sm:w-[400px] h-[550px] rounded-3xl bg-white/80 backdrop-blur-2xl border border-primary-200/50 shadow-2xl overflow-hidden flex flex-col justify-between"
          >
            {/* Header */}
            <div className="p-4 bg-gradient-to-r from-accent-600 to-info-600 text-white flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-yellow-300 animate-pulse" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">AI Admissions Assistant</h4>
                  <span className="text-[10px] text-white/85 font-medium flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-success-400 rounded-full inline-block animate-ping" />
                    Online & Ready
                  </span>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Message Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-primary-50/35">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex gap-2.5 max-w-[80%] ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${msg.sender === "user" ? "bg-accent-500 text-white" : "bg-primary-200 text-primary-700"}`}>
                      {msg.sender === "user" ? <User className="w-3.5 h-3.5" /> : "AI"}
                    </div>
                    <div
                      className={`p-3 rounded-2xl text-sm leading-relaxed shadow-sm overflow-hidden ${
                        msg.sender === "user"
                          ? "bg-accent-600 text-white rounded-tr-none"
                          : "bg-white text-primary-900 border border-primary-200/40 rounded-tl-none prose prose-sm prose-p:my-1 prose-ul:my-1 max-w-none"
                      }`}
                    >
                      {msg.sender === "bot" ? (
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      ) : (
                        msg.text
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="flex gap-2.5 items-center">
                    <div className="w-7 h-7 rounded-full bg-primary-200 flex items-center justify-center text-xs font-bold text-primary-700">
                      AI
                    </div>
                    <div className="p-3 bg-white border border-primary-200/40 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1.5">
                      <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions & Input */}
            <div className="p-3 bg-white border-t border-primary-200/50">
              {/* Chips */}
              {messages.length === 1 && (
                <div className="mb-3">
                  <p className="text-[10px] font-bold text-primary-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <HelpCircle className="w-3 h-3" /> Quick Questions
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {suggestions.map((sug, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSend(sug)}
                        className="text-xs px-2.5 py-1.5 rounded-xl border border-primary-200 hover:border-accent-500 hover:bg-accent-50 text-primary-600 transition-colors"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Input form */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend(inputValue);
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  placeholder="Type your question..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="flex-1 px-4 py-2.5 text-sm rounded-2xl border border-primary-200 focus:outline-none focus:border-accent-500 bg-primary-50/20 focus:bg-white transition-all"
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || loading}
                  className="p-2.5 rounded-2xl bg-gradient-to-r from-accent-500 to-info-500 text-white shadow hover:opacity-90 active:scale-95 disabled:opacity-50 disabled:scale-100 transition-all cursor-pointer"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
