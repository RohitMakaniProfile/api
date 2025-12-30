// src/pages/Index.tsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "../App.css"; // ya jahan tumhara global CSS hai

// ✅ CORRECT
// Fallback hata kar sirf variable rakhein
const BACKEND_URL = import.meta.env.VITE_API_URL || "https://api.wwwrohitmakani.tech";
const API = `${BACKEND_URL}/api`;


const getFullImageUrl = (url: string | null | undefined) => {
  if (!url) return null;
  if (url.startsWith("http") || url.startsWith("data:")) return url;
  return `${BACKEND_URL}/${url}`;
};

const getUserId = () => {
  let userId = localStorage.getItem("luna_user_id");
  if (!userId) {
    userId = `user_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem("luna_user_id", userId);
  }
  return userId;
};

// ---------------- Navigation ----------------

type ViewId = "chat" | "gallery" | "settings";

interface NavigationProps {
  activeView: ViewId;
  setActiveView: (view: ViewId) => void;
  onNewChat: () => void;
}

function Navigation({ activeView, setActiveView, onNewChat }: NavigationProps) {
  return (
    <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50 shadow-2xl">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative group">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-400 via-cyan-500 to-blue-500 p-0.5 transition-transform group-hover:scale-105">
                <div className="w-full h-full rounded-2xl bg-slate-950 flex items-center justify-center">
                  <span className="text-2xl">🌙</span>
                </div>
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-slate-950 animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400">
                Luna AI
              </h1>
              <p className="text-xs text-slate-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                Always here for you
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1 bg-white/5 rounded-full p-1">
            {[
              { id: "chat", icon: "💬", label: "Chat" },
              { id: "gallery", icon: "🖼️", label: "Memories" },
              { id: "settings", icon: "⚙️", label: "Settings" },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id as ViewId)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                  activeView === item.id
                    ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg shadow-emerald-500/20"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <span className="mr-1.5">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>

          {/* New Chat Button */}
          {activeView === "chat" && (
            <button
              onClick={onNewChat}
              className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all hover:scale-105"
            >
              + New Chat
            </button>
          )}
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex gap-2 mt-3">
          {[
            { id: "chat", icon: "💬" },
            { id: "gallery", icon: "🖼️" },
            { id: "settings", icon: "⚙️" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id as ViewId)}
              className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all ${
                activeView === item.id
                  ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white"
                  : "bg-white/5 text-slate-400"
              }`}
            >
              {item.icon}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}

// ---------------- Chat View ----------------

interface ChatMessage {
  role: "user" | "luna";
  content: string;
  photo?: string | null;
  timestamp?: string;
}

interface ChatViewProps {
  userId: string;
}

function ChatView({ userId }: ChatViewProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    void loadChatHistory();
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/history/${userId}`);
      const history = response.data as any[];

      const formattedMessages: ChatMessage[] = history.map((msg) => ({
        role: msg.role === "assistant" ? "luna" : "user",
        content: msg.content,
        photo: msg.photo_sent || msg.image_url,
        timestamp: msg.timestamp,
      }));

      setMessages(formattedMessages);
    } catch (error) {
      console.error("Error loading history:", error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() && !selectedImage) return;

    const userMessage = inputMessage;
    const currentImageForChat = imagePreview;

    setInputMessage("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
        photo: currentImageForChat ?? undefined,
        timestamp: new Date().toISOString(),
      },
    ]);

    setIsLoading(true);

    try {
      let imageAnalysisData: any = null;

      if (selectedImage) {
        const formData = new FormData();
        formData.append("user_id", userId);
        formData.append("file", selectedImage);

        const visionResponse = await axios.post(`${API}/analyze-image`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        imageAnalysisData = visionResponse.data.analysis;

        if (!visionResponse.data.is_safe) {
          setMessages((prev) => [
            ...prev,
            {
              role: "luna",
              content:
                "Hey, I can't process this image. Let's share something else! 🌙",
              timestamp: new Date().toISOString(),
            },
          ]);
          setIsLoading(false);
          setSelectedImage(null);
          setImagePreview(null);
          return;
        }

        setSelectedImage(null);
        setImagePreview(null);
      }

      const chatResponse = await axios.post(`${API}/chat`, {
        user_id: userId,
        message: userMessage,
        imageAnalysis: imageAnalysisData,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "luna",
          content: chatResponse.data.reply,
          photo: chatResponse.data.photo_url,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "luna",
          content: "Oops! Connection hiccup. Let me try again... 🔄",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (ev) =>
        setImagePreview(ev.target?.result as string | null);
      reader.readAsDataURL(file);
    }
  };

  const quickSuggestions = [
    { text: "Tell me something interesting", icon: "💡" },
    { text: "Show me your photo", icon: "📸" },
    { text: "How are you today?", icon: "😊" },
    { text: "Generate a beautiful sunset", icon: "🌅" },
  ];

  return (
    <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
        style={{ maxHeight: "calc(100vh - 240px)" }}
      >
        {messages.length === 0 && (
          <div className="text-center mt-16 animate-in fade-in slide-in-from-bottom duration-700">
            <div className="text-7xl mb-6 animate-float">🌙</div>
            <h2 className="text-3xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400">
              Hey there! I'm Luna
            </h2>
            <p className="text-slate-400 mb-10 max-w-md mx-auto text-lg">
              Your intelligent companion who remembers everything. Share images,
              ask for photos, or just have a conversation!
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto">
              {quickSuggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => setInputMessage(suggestion.text)}
                  className="group p-4 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-500/50 rounded-2xl text-sm text-slate-300 hover:text-white transition-all hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/10"
                >
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">
                    {suggestion.icon}
                  </div>
                  <div className="font-medium">{suggestion.text}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 animate-in fade-in slide-in-from-bottom duration-300 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`w-10 h-10 rounded-2xl shrink-0 flex items-center justify-center text-lg shadow-xl ${
                msg.role === "user"
                  ? "bg-gradient-to-br from-slate-700 to-slate-600"
                  : "bg-gradient-to-br from-emerald-500 to-cyan-500"
              }`}
            >
              {msg.role === "user" ? "👤" : "🌙"}
            </div>

            <div className="max-w-[75%] lg:max-w-[65%] space-y-2">
              <div
                className={`p-4 rounded-2xl shadow-xl backdrop-blur-sm ${
                  msg.role === "user"
                    ? "bg-gradient-to-br from-slate-800/80 to-slate-700/80 text-slate-50 rounded-tr-md border border-slate-700/50"
                    : "bg-gradient-to-br from-emerald-900/30 to-cyan-900/30 border border-emerald-500/20 text-slate-50 rounded-tl-md"
                }`}
              >
                {msg.photo && (
                  <div className="mb-3 rounded-xl overflow-hidden border border-white/10 shadow-lg">
                    <img
                      src={getFullImageUrl(msg.photo) ?? ""}
                      alt="Shared"
                      className="w-full max-w-md hover:scale-105 transition-transform duration-500"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.onerror = null;
                        target.src =
                          "https://placehold.co/400x300/0f172a/10b981?text=Loading";
                      }}
                    />
                  </div>
                )}
                <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {msg.content}
                </p>
              </div>

              <p
                className={`text-xs text-slate-500 px-2 ${
                  msg.role === "user" ? "text-right" : ""
                }`}
              >
                {msg.timestamp
                  ? new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : ""}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 animate-in fade-in slide-in-from-bottom">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-lg shadow-xl">
              🌙
            </div>
            <div className="bg-gradient-to-br from-emerald-900/30 to-cyan-900/30 border border-emerald-500/20 p-4 rounded-2xl rounded-tl-md backdrop-blur-sm">
              <div className="flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.1}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white/5 backdrop-blur-xl border-t border-white/10">
        <div className="max-w-5xl mx-auto">
          {imagePreview && (
            <div className="mb-3 relative inline-block group">
              <img
                src={imagePreview}
                alt="Preview"
                className="h-24 rounded-xl border-2 border-emerald-500/30 shadow-lg"
              />
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setImagePreview(null);
                }}
                className="absolute -top-2 -right-2 bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm hover:bg-red-600 transition shadow-lg group-hover:scale-110"
              >
                ×
              </button>
            </div>
          )}

          <form
            onSubmit={handleSendMessage}
            className="flex gap-2 items-center"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-11 h-11 flex items-center justify-center rounded-xl text-slate-400 hover:text-emerald-400 hover:bg-white/10 transition-all hover:scale-110"
              title="Upload Image"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </button>

            <div className="relative flex-1">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Message Luna..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all placeholder-slate-500 text-white"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || (!inputMessage.trim() && !selectedImage)}
              className="w-11 h-11 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center text-white hover:shadow-lg hover:shadow-emerald-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-110 disabled:hover:scale-100"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 5l7 7-7 7M5 5l7 7-7 7"
                />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

// ---------------- Gallery View ----------------

interface GalleryImage {
  image_url?: string;
  description?: string;
  tags?: string[];
  scene?: string;
}

interface GalleryViewProps {
  userId: string;
}

function GalleryView({ userId }: GalleryViewProps) {
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null);

  useEffect(() => {
    void loadGallery();
  }, []);

  const loadGallery = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API}/gallery/${userId}`, {
        params: searchQuery ? { search: searchQuery } : {},
      });
      setImages(response.data);
    } catch (error) {
      console.error("Error loading gallery:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    void loadGallery();
  };

  return (
    <div className="flex-1 px-4 py-6 max-w-7xl mx-auto w-full">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your memories..."
              className="w-full px-5 py-3 pl-12 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-emerald-500 transition-colors text-white placeholder-slate-500"
            />
            <svg
              className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <button
            type="submit"
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all hover:scale-105"
          >
            Search
          </button>
        </div>
      </form>

      {/* Gallery Grid */}
      {isLoading ? (
        <div className="text-center py-20 text-slate-400">
          <div className="text-5xl mb-4 animate-pulse">🌙</div>
          <p>Loading memories...</p>
        </div>
      ) : images.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <div className="text-6xl mb-4">🖼️</div>
          <p className="text-xl mb-2">No memories yet</p>
          <p className="text-sm">Start chatting and sharing images with Luna!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {images.map((img, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedImage(img)}
              className="group bg-white/5 rounded-2xl overflow-hidden border border-white/10 hover:border-emerald-500/50 transition-all cursor-pointer hover:scale-105 hover:shadow-xl hover:shadow-emerald-500/10"
            >
              {img.image_url && (
                <div className="aspect-square overflow-hidden">
                  <img
                    src={getFullImageUrl(img.image_url) ?? ""}
                    alt={img.description}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    loading="lazy"
                  />
                </div>
              )}
              <div className="p-4">
                <p className="text-sm text-slate-300 mb-2 line-clamp-2">
                  {img.description}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {img.tags?.slice(0, 2).map((tag, tidx) => (
                    <span
                      key={tidx}
                      className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full text-xs border border-emerald-500/30"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div
            className="max-w-4xl w-full bg-slate-900 rounded-2xl overflow-hidden border border-white/20"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={getFullImageUrl(selectedImage.image_url) ?? ""}
              alt={selectedImage.description}
              className="w-full max-h-[70vh] object-contain"
            />
            <div className="p-6">
              <h3 className="text-xl font-semibold mb-2">
                {selectedImage.scene}
              </h3>
              <p className="text-slate-400 mb-4">
                {selectedImage.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {selectedImage.tags?.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-sm border border-emerald-500/30"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------- Settings View ----------------

interface SettingsViewProps {
  userId: string;
}

function SettingsView({ userId }: SettingsViewProps) {
  const [stats, setStats] = useState({ totalMessages: 0, totalImages: 0 });

  useEffect(() => {
    void loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [historyRes, galleryRes] = await Promise.all([
        axios.get(`${API}/history/${userId}`),
        axios.get(`${API}/gallery/${userId}`),
      ]);
      setStats({
        totalMessages: historyRes.data.length,
        totalImages: galleryRes.data.length,
      });
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const handleClearHistory = () => {
    if (window.confirm("Are you sure you want to clear all chat history?")) {
      // Needs backend endpoint
      alert("Feature coming soon!");
    }
  };

  return (
    <div className="flex-1 px-4 py-6 max-w-4xl mx-auto w-full">
      <h2 className="text-3xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400">
        Settings
      </h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 rounded-2xl p-6">
          <div className="text-3xl mb-2">💬</div>
          <div className="text-2xl font-bold text-white">
            {stats.totalMessages}
          </div>
          <div className="text-sm text-slate-400">Total Messages</div>
        </div>
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-2xl p-6">
          <div className="text-3xl mb-2">🖼️</div>
          <div className="text-2xl font-bold text-white">
            {stats.totalImages}
          </div>
          <div className="text-sm text-slate-400">Stored Memories</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-6">
          <div className="text-3xl mb-2">👤</div>
          <div className="text-sm font-mono text-white">
            {userId.substring(0, 12)}...
          </div>
          <div className="text-sm text-slate-400">Your User ID</div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="space-y-4">
        {/* Account Section */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>👤</span> Account
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">User ID</span>
              <span className="font-mono text-slate-300">{userId}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Storage</span>
              <span className="text-emerald-400">Local File System</span>
            </div>
          </div>
        </div>

        {/* Privacy Section */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>🔒</span> Privacy & Data
          </h3>
          <div className="space-y-3">
            <button
              onClick={handleClearHistory}
              className="w-full px-4 py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 font-medium transition-all"
            >
              Clear Chat History
            </button>
            <p className="text-xs text-slate-500">
              All your data is stored locally on your device. Luna respects your
              privacy.
            </p>
          </div>
        </div>

        {/* About Section */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>ℹ️</span> About Luna AI
          </h3>
          <div className="space-y-2 text-sm text-slate-400">
            <p>Version: 1.0.0</p>
            <p>Powered by Google Gemini 2.0 Flash</p>
            <p>Built with FastAPI + React</p>
            <p className="pt-3 text-xs">
              Made with ❤️ for meaningful AI conversations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------- Main Index (page) ----------------

const Index: React.FC = () => {
  const [userId] = useState<string>(getUserId());
  const [activeView, setActiveView] = useState<ViewId>("chat");

  const handleNewChat = () => {
    if (
      window.confirm(
        "Start a new conversation? (Current chat will be saved)"
      )
    ) {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white font-sans flex flex-col">
      <Navigation
        activeView={activeView}
        setActiveView={setActiveView}
        onNewChat={handleNewChat}
      />

      {activeView === "chat" && <ChatView userId={userId} />}
      {activeView === "gallery" && <GalleryView userId={userId} />}
      {activeView === "settings" && <SettingsView userId={userId} />}

      <footer className="text-center py-4 text-xs text-slate-600 border-t border-white/5">
        Luna AI • Your Intelligent Companion • Privacy-First Design
      </footer>
    </div>
  );
};

export default Index;
