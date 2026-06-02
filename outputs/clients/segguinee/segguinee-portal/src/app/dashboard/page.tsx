"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// ── Types ──────────────────────────────────────────────────────────────────

interface Conversation {
  id: string; phone: string; profile_name: string;
  last_message: string; last_message_at: string;
  unread_count: number; status: string; is_director: boolean;
}
interface Message {
  id: string; conversation_phone: string;
  direction: "inbound" | "outbound"; body: string;
  action: string; ai_generated: boolean; created_at: string;
}
interface ProductionEntry {
  id: string; volume_m3: number; station: string;
  zone: string; recorded_by: string; recorded_at: string;
}
interface Invoice {
  id: string; customer_phone: string; customer_name: string;
  amount_gnf: number; reference: string; description: string; due_date: string;
  status: "pending" | "paid" | "overdue" | "cancelled";
  signed: boolean; paid_at: string | null; created_at: string;
}
interface Incident {
  id: string; type: string; description: string;
  zone: string; station: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  reported_by: string; created_at: string;
}

type Tab = "conversations" | "production" | "invoices" | "incidents" | "projects" | "agents" | "terrain";

// ── Design tokens ─────────────────────────────────────────────────────────

const T = {
  canvas: "#0F172A", surface: "#1E293B", surfaceHover: "#273449",
  border: "#334155", accent: "#3B82F6", accentDim: "rgba(59,130,246,.15)",
  text: "#F8FAFC", text2: "#CBD5E1", text3: "#94A3B8", subtle: "#64748B",
  success: "#34D399", successDim: "rgba(52,211,153,.15)",
  warning: "#FBBF24", warningDim: "rgba(251,191,36,.15)",
  danger: "#F87171", dangerDim: "rgba(248,113,113,.15)",
};

const ZONES = ["Kaloum", "Dixinn", "Matam", "Ratoma", "Matoto", "Coyah", "Dubréka", "Kindia"];
const INCIDENT_TYPES = ["rupture", "panne", "contamination", "fuite", "autre"];

// ── Helpers ───────────────────────────────────────────────────────────────

function invoiceStatusBadge(s: string) {
  const map: Record<string, { label: string; bg: string; c: string }> = {
    pending:   { label: "En attente", bg: T.warningDim, c: T.warning },
    paid:      { label: "Payée",      bg: T.successDim, c: T.success },
    overdue:   { label: "En retard",  bg: T.dangerDim,  c: T.danger  },
    cancelled: { label: "Annulée",    bg: T.surface,    c: T.text3   },
  };
  const b = map[s] || map.pending;
  return <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: b.bg, color: b.c }}>{b.label}</span>;
}

function incidentStatusBadge(s: string) {
  const map: Record<string, { label: string; bg: string; c: string }> = {
    open:        { label: "Ouvert",   bg: T.dangerDim,  c: T.danger  },
    in_progress: { label: "En cours", bg: T.warningDim, c: T.warning },
    resolved:    { label: "Résolu",   bg: T.successDim, c: T.success },
    closed:      { label: "Fermé",    bg: T.surface,    c: T.text3   },
  };
  const b = map[s] || map.open;
  return <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: b.bg, color: b.c }}>{b.label}</span>;
}

function formatTime(iso: string) {
  if (!iso) return "";
  const d = new Date(iso); const now = new Date();
  return d.toDateString() === now.toDateString()
    ? d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
    : d.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
}
function formatDate(iso: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}
function formatGNF(n: number) { return n.toLocaleString("fr-FR") + " GNF"; }

const tabs: { key: Tab; label: string; icon: string }[] = [
  { key: "conversations", label: "Conversations", icon: "💬" },
  { key: "production",    label: "Production",    icon: "📊" },
  { key: "invoices",      label: "Factures",      icon: "📄" },
  { key: "incidents",     label: "Incidents",     icon: "🚨" },
  { key: "projects",      label: "Projets",       icon: "🏗️" },
  { key: "terrain",       label: "Terrain",       icon: "👷" },
  { key: "agents",        label: "Agents IA",     icon: "🤖" },
];

const PROJECT_TYPES   = ["construction", "réhabilitation", "extension", "maintenance", "étude"];
const PROJECT_STATUTS = ["planifié", "en_cours", "terminé", "suspendu"];

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  DASHBOARD                                                              ║
// ╚══════════════════════════════════════════════════════════════════════════╝

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [authed, setAuthed] = useState(false);
  const [tab, setTab] = useState<Tab>("conversations");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    if (document.cookie.includes("segguinee_auth=")) setAuthed(true);
    else router.push("/login");
  }, [router]);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam && tabs.some(t => t.key === tabParam)) {
      setTab(tabParam as Tab);
    }
  }, [searchParams]);

  const handleTabChange = (newTab: Tab) => {
    setTab(newTab);
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", newTab);
    router.push(`?${params.toString()}`, { scroll: false });
  };

  if (!authed) return null;

  const logout = () => { document.cookie = "segguinee_auth=; path=/; max-age=0"; router.push("/login"); };

  return (
    <div style={{ display: "flex", height: "100dvh", background: T.canvas, color: T.text, overflow: "hidden" }}>

      {/* ── SIDEBAR — desktop visible, mobile drawer ──────────────────── */}
      {!isMobile && (
      <aside
        style={{ width: 220, background: T.surface, borderRight: `1px solid ${T.border}`, display: "flex", flexDirection: "column", flexShrink: 0 }}>

        {/* Brand */}
        <div style={{ padding: "20px 20px 16px", borderBottom: `1px solid ${T.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 32, height: 32, background: "rgba(59,130,246,0.15)",
              borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="#3B82F6">
                <path d="M12 2C12 2 4 12.5 4 17a8 8 0 1 0 16 0C20 12.5 12 2 12 2Z"/>
              </svg>
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: T.text, letterSpacing: "-0.01em" }}>SEGGUINÉE</div>
              <div style={{ fontSize: 10, color: T.subtle, marginTop: 1 }}>Portail Opérateur</div>
            </div>
          </div>
        </div>

        {/* Nav items */}
        <nav style={{ flex: 1, overflowY: "auto", padding: "12px 8px" }}>
          {/* Group labels */}
          {[
            { label: "OPÉRATIONS",    keys: ["conversations", "production", "terrain"] as Tab[] },
            { label: "FINANCE",       keys: ["invoices"] as Tab[] },
            { label: "INFRASTRUCTURE",keys: ["incidents", "projects"] as Tab[] },
            { label: "SYSTÈME",       keys: ["agents"] as Tab[] },
          ].map(group => (
            <div key={group.label} style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em",
                color: T.subtle, padding: "0 12px", marginBottom: 4 }}>
                {group.label}
              </div>
              {group.keys.map(key => {
                const t = tabs.find(x => x.key === key)!;
                const active = tab === key;
                return (
                  <button key={key} onClick={() => handleTabChange(key)}
                    style={{
                      width: "100%", display: "flex", alignItems: "center", gap: 10,
                      padding: "8px 12px", borderRadius: 8, border: "none", cursor: "pointer",
                      background: active ? T.canvas : "transparent",
                      color: active ? T.text : T.text3,
                      borderLeft: active ? `2px solid ${T.accent}` : "2px solid transparent",
                      marginBottom: 2, transition: "all 150ms",
                      fontFamily: "inherit", textAlign: "left",
                    }}
                    onMouseEnter={e => { if (!active) { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.color = T.text2; } }}
                    onMouseLeave={e => { if (!active) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = T.text3; } }}>
                    <span style={{ fontSize: 15, lineHeight: 1, width: 20, textAlign: "center", flexShrink: 0 }}>{t.icon}</span>
                    <span style={{ fontSize: 13, fontWeight: active ? 600 : 400 }}>{t.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Logout */}
        <div style={{ padding: "12px 8px", borderTop: `1px solid ${T.border}` }}>
          <button onClick={logout}
            style={{ width: "100%", display: "flex", alignItems: "center", gap: 10,
              padding: "8px 12px", borderRadius: 8, border: "none", cursor: "pointer",
              background: "transparent", color: T.text3, fontFamily: "inherit", transition: "all 150ms" }}
            onMouseEnter={e => { e.currentTarget.style.background = "rgba(248,113,113,0.08)"; e.currentTarget.style.color = T.danger; }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = T.text3; }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span style={{ fontSize: 13 }}>Déconnexion</span>
          </button>
        </div>
      </aside>
      )}

      {/* ── MAIN AREA ───────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, overflow: "hidden" }}>

        {/* Mobile header */}
        {isMobile && (
        <header
          style={{ borderColor: T.border, background: T.surface, borderBottom: `1px solid ${T.border}`, padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", position: "relative", zIndex: 40 }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: "none", border: "none", cursor: "pointer", padding: "4px", color: T.text }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 26, height: 26, background: "rgba(59,130,246,0.15)",
              borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="#3B82F6">
                <path d="M12 2C12 2 4 12.5 4 17a8 8 0 1 0 16 0C20 12.5 12 2 12 2Z"/>
              </svg>
            </div>
            <span className="text-sm font-bold tracking-tight">SEGGUINÉE</span>
          </div>
          <button onClick={logout} className="text-xs px-3 py-1.5 rounded-md"
            style={{ background: T.canvas, color: T.text3 }}>Sortir</button>
        </header>
        )}

        {/* Mobile drawer backdrop + sidebar */}
        {isMobile && sidebarOpen && (
          <>
            <div onClick={() => setSidebarOpen(false)}
              style={{
                position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
                background: "rgba(0,0,0,0.5)", zIndex: 35
              }} />
            <aside style={{
              position: "fixed", top: 0, left: 0, bottom: 0, width: 220,
              background: T.surface, borderRight: `1px solid ${T.border}`,
              zIndex: 40, display: "flex", flexDirection: "column",
              animation: "slideIn 200ms ease-out",
              overflow: "hidden"
            }}>
              <style>{`@keyframes slideIn { from { transform: translateX(-100%); } to { transform: translateX(0); } }`}</style>

              {/* Brand */}
              <div style={{ padding: "20px 20px 16px", borderBottom: `1px solid ${T.border}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 32, height: 32, background: "rgba(59,130,246,0.15)",
                    borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#3B82F6">
                      <path d="M12 2C12 2 4 12.5 4 17a8 8 0 1 0 16 0C20 12.5 12 2 12 2Z"/>
                    </svg>
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: T.text, letterSpacing: "-0.01em" }}>SEGGUINÉE</div>
                    <div style={{ fontSize: 10, color: T.subtle, marginTop: 1 }}>Portail Opérateur</div>
                  </div>
                </div>
              </div>

              {/* Nav items */}
              <nav style={{ flex: 1, overflowY: "auto", padding: "12px 8px" }}>
                {[
                  { label: "OPÉRATIONS",    keys: ["conversations", "production", "terrain"] as Tab[] },
                  { label: "FINANCE",       keys: ["invoices"] as Tab[] },
                  { label: "INFRASTRUCTURE",keys: ["incidents", "projects"] as Tab[] },
                  { label: "SYSTÈME",       keys: ["agents"] as Tab[] },
                ].map(group => (
                  <div key={group.label} style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em",
                      color: T.subtle, padding: "0 12px", marginBottom: 4 }}>
                      {group.label}
                    </div>
                    {group.keys.map(key => {
                      const t = tabs.find(x => x.key === key)!;
                      const active = tab === key;
                      return (
                        <button key={key} onClick={() => { handleTabChange(key); setSidebarOpen(false); }}
                          style={{
                            width: "100%", display: "flex", alignItems: "center", gap: 10,
                            padding: "8px 12px", borderRadius: 8, border: "none", cursor: "pointer",
                            background: active ? T.canvas : "transparent",
                            color: active ? T.text : T.text3,
                            borderLeft: active ? `2px solid ${T.accent}` : "2px solid transparent",
                            marginBottom: 2, transition: "all 150ms",
                            fontFamily: "inherit", textAlign: "left",
                          }}>
                          <span style={{ fontSize: 15, lineHeight: 1, width: 20, textAlign: "center", flexShrink: 0 }}>{t.icon}</span>
                          <span style={{ fontSize: 13, fontWeight: active ? 600 : 400 }}>{t.label}</span>
                        </button>
                      );
                    })}
                  </div>
                ))}
              </nav>

              {/* Logout */}
              <div style={{ padding: "12px 8px", borderTop: `1px solid ${T.border}` }}>
                <button onClick={() => { logout(); setSidebarOpen(false); }}
                  style={{ width: "100%", display: "flex", alignItems: "center", gap: 10,
                    padding: "8px 12px", borderRadius: 8, border: "none", cursor: "pointer",
                    background: "transparent", color: T.text3, fontFamily: "inherit", transition: "all 150ms" }}>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  <span style={{ fontSize: 13 }}>Déconnexion</span>
                </button>
              </div>
            </aside>
          </>
        )}

        {/* Panel content */}
        <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
          {tab === "conversations" && <ConversationsPanel />}
          {tab === "production"    && <ProductionPanel />}
          {tab === "invoices"      && <InvoicesPanel />}
          {tab === "incidents"     && <IncidentsPanel />}
          {tab === "projects"      && <ProjectsPanel />}
          {tab === "terrain"       && <TerrainPanel />}
          {tab === "agents"        && <AgentsPanel />}
        </div>
      </div>
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  CONVERSATIONS                                                          ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function ConversationsPanel() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [mobileView, setMobileView] = useState<"list" | "thread">("list");

  const loadConversations = useCallback(async () => {
    const res = await fetch("/api/data/conversations");
    if (res.ok) setConversations(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => {
    loadConversations();
    const t = setInterval(loadConversations, 30000);
    return () => clearInterval(t);
  }, [loadConversations]);

  useEffect(() => {
    if (!selected) return;
    const load = async () => {
      const res = await fetch(`/api/data/messages?phone=${encodeURIComponent(selected.phone)}`);
      if (res.ok) setMessages(await res.json());
    };
    load();
    fetch("/api/data/conversations", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: selected.id, Unread_count: 0 }),
    });
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [selected]);

  return (
    <div className="flex h-full">
      {/* Sidebar — full width on mobile when in list view, hidden when in thread view */}
      <aside
        className={`flex-shrink-0 border-r flex flex-col ${mobileView === "thread" ? "hidden md:flex" : "flex"} w-full md:w-80 lg:w-96`}
        style={{ borderColor: T.border }}>
        <div className="flex-1 overflow-y-auto">
          {loading && [1,2,3].map(i => (
            <div key={i} className="p-4 animate-pulse border-b" style={{ borderColor: T.border }}>
              <div className="h-4 w-2/3 rounded mb-2" style={{ background: T.surface }} />
              <div className="h-3 w-full rounded" style={{ background: T.surface }} />
            </div>
          ))}
          {!loading && conversations.length === 0 && (
            <div className="p-8 text-center">
              <p className="text-sm" style={{ color: T.text3 }}>Aucune conversation WhatsApp</p>
              <p className="text-xs mt-2" style={{ color: T.subtle }}>Les messages arriveront ici automatiquement</p>
            </div>
          )}
          {conversations.map(c => (
            <button key={c.id} onClick={() => { setSelected(c); setMobileView("thread"); }}
              className="w-full text-left p-4 border-b transition-colors"
              style={{ background: selected?.id === c.id ? T.surface : T.canvas, borderColor: T.border }}>
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium truncate">{c.profile_name || c.phone}</span>
                    {c.is_director && <span className="text-[10px] px-1.5 py-0.5 rounded-full font-medium" style={{ background: T.accentDim, color: T.accent }}>Directeur</span>}
                  </div>
                  <p className="text-xs truncate mt-0.5" style={{ color: T.text3 }}>{c.last_message}</p>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <span className="text-[10px]" style={{ color: T.text3 }}>{formatTime(c.last_message_at)}</span>
                  {c.unread_count > 0 && (
                    <span className="text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-bold" style={{ background: T.accent }}>{c.unread_count}</span>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </aside>

      {/* Thread — hidden on mobile when in list view */}
      <main className={`flex-1 flex flex-col min-w-0 ${mobileView === "list" ? "hidden md:flex" : "flex"}`}>
        {/* Mobile back button */}
        <button
          onClick={() => setMobileView("list")}
          className="md:hidden flex items-center gap-2 px-4 py-3 border-b text-xs font-medium"
          style={{ borderColor: T.border, color: T.text3 }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Retour aux conversations
        </button>
        {!selected ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke={T.border} strokeWidth="1" strokeLinecap="round">
                <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" />
              </svg>
              <p className="text-sm font-medium" style={{ color: T.text3 }}>Sélectionnez une conversation</p>
            </div>
          </div>
        ) : (
          <>
            <div className="p-4 border-b flex items-center justify-between" style={{ borderColor: T.border }}>
              <div>
                <p className="text-sm font-semibold">{selected.profile_name || selected.phone}</p>
                <p className="text-xs font-mono" style={{ color: T.text3 }}>{selected.phone}</p>
              </div>
              {selected.is_director && <span className="text-xs px-3 py-1 rounded-full font-medium" style={{ background: T.accentDim, color: T.accent }}>Directeur</span>}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.direction === "outbound" ? "justify-end" : "justify-start"}`}>
                  <div className="max-w-[75%] rounded-xl px-4 py-2.5" style={{ background: m.direction === "outbound" ? T.accent : T.surface }}>
                    <p className="text-sm whitespace-pre-wrap">{m.body}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] opacity-60">{formatTime(m.created_at)}</span>
                      {m.ai_generated && <span className="text-[10px] opacity-50">🤖 AI</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  PRODUCTION                                                             ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function ProductionPanel() {
  const [data, setData] = useState<ProductionEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ volume_m3: "", station: "", zone: "", recorded_by: "" });
  const u = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    const res = await fetch("/api/data/production");
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.BaseSyntheticEvent) => {
    e.preventDefault();
    setSaving(true);
    await fetch("/api/data/production", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaving(false);
    setShowModal(false);
    setForm({ volume_m3: "", station: "", zone: "", recorded_by: "" });
    load();
  };

  const totalM3 = data.reduce((s, e) => s + (e.volume_m3 || 0), 0);

  return (
    <div className="p-4 md:p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold">Relevés de production</h2>
          <p className="text-xs mt-0.5" style={{ color: T.text3 }}>{data.length} relevé{data.length !== 1 ? "s" : ""} enregistré{data.length !== 1 ? "s" : ""}</p>
        </div>
        <AddButton onClick={() => setShowModal(true)}>Ajouter relevé</AddButton>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label="Volume Total (m³)" value={totalM3.toLocaleString("fr-FR")} />
        <KpiCard label="Stations Actives"  value={String(new Set(data.map(d => d.station).filter(Boolean)).size)} />
        <KpiCard label="Relevés Aujourd'hui" value={String(data.filter(d => new Date(d.recorded_at).toDateString() === new Date().toDateString()).length)} />
      </div>

      <DataTable loading={loading} empty="Aucun relevé de production"
        headers={["Volume (m³)", "Station", "Zone", "Date", "Enregistré par"]}
        rows={data.map(d => [
          <span key="v" className="font-mono font-semibold">{d.volume_m3.toLocaleString("fr-FR")}</span>,
          d.station || "—", d.zone || "—",
          <span key="d" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.recorded_at)}</span>,
          <span key="b" className="text-[11px] font-mono" style={{ color: T.text3 }}>{d.recorded_by || "—"}</span>,
        ])}
      />

      {showModal && (
        <Modal title="Ajouter un relevé de production" onClose={() => setShowModal(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField label="Volume (m³) *">
              <input type="number" required min="0" step="0.01" placeholder="1250"
                value={form.volume_m3} onChange={e => u("volume_m3", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Station *">
                <input type="text" required placeholder="Kaloum"
                  value={form.station} onChange={e => u("station", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
              <FormField label="Zone">
                <select value={form.zone} onChange={e => u("zone", e.target.value)}
                  className={inputCls} style={inputStyle}>
                  <option value="">Sélectionner</option>
                  {ZONES.map(z => <option key={z} value={z}>{z}</option>)}
                </select>
              </FormField>
            </div>
            <FormField label="Enregistré par">
              <input type="text" placeholder="Nom ou téléphone"
                value={form.recorded_by} onChange={e => u("recorded_by", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <ModalActions onCancel={() => setShowModal(false)} saving={saving} label="Enregistrer" />
          </form>
        </Modal>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  INVOICES                                                               ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function InvoicesPanel() {
  const [data, setData] = useState<Invoice[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ customer_phone: "", customer_name: "", amount_gnf: "", description: "", due_date: "" });
  const u = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    setLoading(true);
    const res = await fetch(`/api/data/invoices?status=${filter}`);
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.BaseSyntheticEvent) => {
    e.preventDefault();
    setSaving(true);
    await fetch("/api/data/invoices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaving(false);
    setShowModal(false);
    setForm({ customer_phone: "", customer_name: "", amount_gnf: "", description: "", due_date: "" });
    load();
  };

  const pending = data.filter(i => i.status === "pending").reduce((s, i) => s + i.amount_gnf, 0);
  const paid    = data.filter(i => i.status === "paid").reduce((s, i) => s + i.amount_gnf, 0);

  return (
    <div className="p-4 md:p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold">Factures</h2>
          <p className="text-xs mt-0.5" style={{ color: T.text3 }}>{data.length} facture{data.length !== 1 ? "s" : ""}</p>
        </div>
        <AddButton onClick={() => setShowModal(true)}>Ajouter facture</AddButton>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label="En Attente (GNF)" value={formatGNF(pending)} color={T.warning} />
        <KpiCard label="Payé (GNF)"       value={formatGNF(paid)}    color={T.success} />
        <KpiCard label="Total Factures"   value={String(data.length)} />
      </div>

      <div className="flex gap-2 mb-4 overflow-x-auto pb-1" style={{ scrollbarWidth: "none" }}>
        {[{ k:"all",l:"Toutes" },{ k:"pending",l:"En attente" },{ k:"paid",l:"Payées" },{ k:"overdue",l:"En retard" }].map(f => (
          <button key={f.k} onClick={() => setFilter(f.k)}
            className="text-xs px-3 py-1.5 rounded-md transition-colors"
            style={{ background: filter === f.k ? T.accent : T.surface, color: filter === f.k ? T.text : T.text3 }}>
            {f.l}
          </button>
        ))}
      </div>

      <DataTable loading={loading} empty="Aucune facture"
        headers={["Référence", "Client", "Montant", "Échéance", "Signé", "Statut"]}
        rows={data.map(d => [
          <span key="r" className="font-mono text-[11px]">{d.reference || "—"}</span>,
          <span key="c" className="text-xs">{d.customer_name || d.customer_phone || "—"}</span>,
          <span key="m" className="font-mono font-semibold">{d.amount_gnf.toLocaleString("fr-FR")} GNF</span>,
          <span key="e" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.due_date)}</span>,
          d.signed
            ? <span key="s" className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: T.successDim, color: T.success }}>✓ Signé</span>
            : <span key="s" className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: T.surface, color: T.text3 }}>En attente</span>,
          invoiceStatusBadge(d.status),
        ])}
      />

      {showModal && (
        <Modal title="Ajouter une facture" onClose={() => setShowModal(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField label="Téléphone client *">
              <input type="text" required placeholder="628123456"
                value={form.customer_phone} onChange={e => u("customer_phone", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <FormField label="Nom client">
              <input type="text" placeholder="Mohamed Soumah"
                value={form.customer_name} onChange={e => u("customer_name", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Montant (GNF) *">
                <input type="number" required min="0" placeholder="500000"
                  value={form.amount_gnf} onChange={e => u("amount_gnf", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
              <FormField label="Date d'échéance">
                <input type="date"
                  value={form.due_date} onChange={e => u("due_date", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
            </div>
            <FormField label="Description">
              <input type="text" placeholder="Eau potable — juin 2026"
                value={form.description} onChange={e => u("description", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <div className="rounded-lg px-3 py-2.5 flex items-start gap-2" style={{ background: "rgba(59,130,246,.08)", border: "1px solid rgba(59,130,246,.2)" }}>
              <span style={{ color: T.accent, fontSize: 15, lineHeight: 1.4 }}>✉</span>
              <p className="text-xs leading-relaxed" style={{ color: T.text2 }}>
                Un lien de signature sera envoyé au client via WhatsApp dès la création.
              </p>
            </div>
            <ModalActions onCancel={() => setShowModal(false)} saving={saving} label="Créer et envoyer" />
          </form>
        </Modal>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  INCIDENTS                                                              ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function IncidentsPanel() {
  const [data, setData] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ type: "panne", description: "", zone: "", station: "", reported_by: "" });
  const u = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    const res = await fetch("/api/data/incidents");
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.BaseSyntheticEvent) => {
    e.preventDefault();
    setSaving(true);
    await fetch("/api/data/incidents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaving(false);
    setShowModal(false);
    setForm({ type: "panne", description: "", zone: "", station: "", reported_by: "" });
    load();
  };

  const active = data.filter(i => i.status === "open" || i.status === "in_progress").length;

  return (
    <div className="p-4 md:p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold">Incidents</h2>
          <p className="text-xs mt-0.5" style={{ color: T.text3 }}>{active} actif{active !== 1 ? "s" : ""} · {data.length} total</p>
        </div>
        <AddButton onClick={() => setShowModal(true)}>Signaler incident</AddButton>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label="Incidents Actifs" value={String(active)} color={active > 0 ? T.danger : T.success} />
        <KpiCard label="Total Signalés"   value={String(data.length)} />
        <KpiCard label="Résolus"          value={String(data.filter(i => i.status === "resolved" || i.status === "closed").length)} color={T.success} />
      </div>

      <DataTable loading={loading} empty="Aucun incident signalé"
        headers={["Type", "Description", "Zone", "Date", "Statut"]}
        rows={data.map(d => [
          <span key="t" className="text-xs font-medium capitalize">{d.type || "—"}</span>,
          <span key="d" className="text-xs">{(d.description||"").slice(0,60)}{(d.description||"").length > 60 ? "…" : ""}</span>,
          <span key="z" className="text-xs">{d.zone || d.station || "—"}</span>,
          <span key="dt" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.created_at)}</span>,
          incidentStatusBadge(d.status),
        ])}
      />

      {showModal && (
        <Modal title="Signaler un incident" onClose={() => setShowModal(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField label="Type d'incident *">
              <select required value={form.type} onChange={e => u("type", e.target.value)}
                className={inputCls} style={inputStyle}>
                {INCIDENT_TYPES.map(t => (
                  <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Description *">
              <textarea required rows={3} placeholder="Décrivez l'incident..."
                value={form.description} onChange={e => u("description", e.target.value)}
                className={inputCls} style={{ ...inputStyle, resize: "none" }} />
            </FormField>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Zone">
                <select value={form.zone} onChange={e => u("zone", e.target.value)}
                  className={inputCls} style={inputStyle}>
                  <option value="">Sélectionner</option>
                  {ZONES.map(z => <option key={z} value={z}>{z}</option>)}
                </select>
              </FormField>
              <FormField label="Station">
                <input type="text" placeholder="Station concernée"
                  value={form.station} onChange={e => u("station", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
            </div>
            <FormField label="Signalé par">
              <input type="text" placeholder="Nom ou téléphone"
                value={form.reported_by} onChange={e => u("reported_by", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <ModalActions onCancel={() => setShowModal(false)} saving={saving} label="Signaler" />
          </form>
        </Modal>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  PROJECTS                                                               ║
// ╚══════════════════════════════════════════════════════════════════════════╝

interface Project {
  id: string; nom: string; type: string; zone: string; statut: string;
  budget_gnf: number; depense_gnf: number; date_debut: string; date_fin: string;
  chef_projet: string; description: string; created_at: string;
}

function projectStatutStyle(s: string): { bg: string; c: string; label: string } {
  return ({
    "planifié":  { bg: T.accentDim,  c: T.accent,   label: "Planifié"  },
    "en_cours":  { bg: T.warningDim, c: T.warning,  label: "En cours"  },
    "terminé":   { bg: T.successDim, c: T.success,  label: "Terminé"   },
    "suspendu":  { bg: T.dangerDim,  c: T.danger,   label: "Suspendu"  },
  }[s] ?? { bg: T.surface, c: T.text3, label: s });
}

function ProjectsPanel() {
  const [data, setData] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filterStatut, setFilterStatut] = useState("all");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    nom: "", type: "construction", zone: "", statut: "planifié",
    budget_gnf: "", depense_gnf: "", date_debut: "", date_fin: "",
    chef_projet: "", description: "",
  });
  const u = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    const res = await fetch("/api/data/projects");
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.BaseSyntheticEvent) => {
    e.preventDefault();
    setSaving(true);
    await fetch("/api/data/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaving(false);
    setShowModal(false);
    setForm({ nom: "", type: "construction", zone: "", statut: "planifié", budget_gnf: "", depense_gnf: "", date_debut: "", date_fin: "", chef_projet: "", description: "" });
    load();
  };

  const filtered = filterStatut === "all" ? data : data.filter(p => p.statut === filterStatut);
  const actifs   = data.filter(p => p.statut === "en_cours").length;
  const termines = data.filter(p => p.statut === "terminé").length;
  const budgetTotal = data.reduce((s, p) => s + (p.budget_gnf || 0), 0);

  return (
    <div className="p-4 md:p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold">Projets</h2>
          <p className="text-xs mt-0.5" style={{ color: T.text3 }}>{data.length} projet{data.length !== 1 ? "s" : ""} · {actifs} en cours</p>
        </div>
        <AddButton onClick={() => setShowModal(true)}>Ajouter projet</AddButton>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label="En cours"      value={String(actifs)}   color={T.warning} />
        <KpiCard label="Terminés"      value={String(termines)} color={T.success} />
        <KpiCard label="Total projets" value={String(data.length)} />
        <KpiCard label="Budget total"  value={budgetTotal > 0 ? formatGNF(budgetTotal) : "—"} />
      </div>

      {/* Status filter */}
      <div className="flex gap-2 mb-5">
        {[{ k:"all",l:"Tous" },{ k:"planifié",l:"Planifiés" },{ k:"en_cours",l:"En cours" },{ k:"terminé",l:"Terminés" },{ k:"suspendu",l:"Suspendus" }].map(f => (
          <button key={f.k} onClick={() => setFilterStatut(f.k)}
            className="text-xs px-3 py-1.5 rounded-md transition-colors"
            style={{ background: filterStatut === f.k ? T.accent : T.surface, color: filterStatut === f.k ? T.text : T.text3 }}>
            {f.l}
          </button>
        ))}
      </div>

      {/* Project cards */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1,2,3].map(i => (
            <div key={i} className="rounded-xl p-5 animate-pulse" style={{ background: T.surface, border: `1px solid ${T.border}` }}>
              <div className="h-4 w-2/3 rounded mb-3" style={{ background: T.border }} />
              <div className="h-3 w-full rounded mb-2" style={{ background: T.border }} />
              <div className="h-3 w-1/2 rounded" style={{ background: T.border }} />
            </div>
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20">
          <span className="text-4xl mb-4">🏗️</span>
          <p className="text-sm font-medium" style={{ color: T.text3 }}>Aucun projet{filterStatut !== "all" ? " dans ce statut" : ""}</p>
          <p className="text-xs mt-1" style={{ color: T.subtle }}>Cliquez sur « Ajouter projet » pour commencer</p>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(p => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <Modal title="Ajouter un projet" onClose={() => setShowModal(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField label="Nom du projet *">
              <input type="text" required placeholder="Extension réseau Ratoma"
                value={form.nom} onChange={e => u("nom", e.target.value)}
                className={inputCls} style={inputStyle} />
            </FormField>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Type *">
                <select required value={form.type} onChange={e => u("type", e.target.value)}
                  className={inputCls} style={inputStyle}>
                  {PROJECT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
              </FormField>
              <FormField label="Statut">
                <select value={form.statut} onChange={e => u("statut", e.target.value)}
                  className={inputCls} style={inputStyle}>
                  {PROJECT_STATUTS.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1).replace("_"," ")}</option>)}
                </select>
              </FormField>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Zone">
                <select value={form.zone} onChange={e => u("zone", e.target.value)}
                  className={inputCls} style={inputStyle}>
                  <option value="">Sélectionner</option>
                  {[...ZONES, "Plusieurs zones"].map(z => <option key={z} value={z}>{z}</option>)}
                </select>
              </FormField>
              <FormField label="Chef de projet">
                <input type="text" placeholder="Mamadou Diallo"
                  value={form.chef_projet} onChange={e => u("chef_projet", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Budget (GNF)">
                <input type="number" min="0" placeholder="5000000"
                  value={form.budget_gnf} onChange={e => u("budget_gnf", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
              <FormField label="Dépensé (GNF)">
                <input type="number" min="0" placeholder="0"
                  value={form.depense_gnf} onChange={e => u("depense_gnf", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Date de début">
                <input type="date" value={form.date_debut} onChange={e => u("date_debut", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
              <FormField label="Date de fin prévue">
                <input type="date" value={form.date_fin} onChange={e => u("date_fin", e.target.value)}
                  className={inputCls} style={inputStyle} />
              </FormField>
            </div>
            <FormField label="Description">
              <textarea rows={2} placeholder="Objectifs et périmètre du projet..."
                value={form.description} onChange={e => u("description", e.target.value)}
                className={inputCls} style={{ ...inputStyle, resize: "none" }} />
            </FormField>
            <ModalActions onCancel={() => setShowModal(false)} saving={saving} label="Créer le projet" />
          </form>
        </Modal>
      )}
    </div>
  );
}

function ProjectCard({ project: p }: { project: Project }) {
  const statut = projectStatutStyle(p.statut);
  const hasBudget = p.budget_gnf > 0;
  const pct = hasBudget ? Math.min(100, Math.round((p.depense_gnf / p.budget_gnf) * 100)) : 0;
  const barColor = pct > 90 ? T.danger : pct > 70 ? T.warning : T.success;

  return (
    <div className="rounded-xl p-5 flex flex-col gap-3 transition-colors"
      style={{ background: T.surface, border: `1px solid ${T.border}` }}
      onMouseEnter={e => (e.currentTarget.style.borderColor = T.accent + "66")}
      onMouseLeave={e => (e.currentTarget.style.borderColor = T.border)}>

      {/* Title row */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold leading-tight truncate">{p.nom}</h3>
          {p.zone && <p className="text-[11px] mt-0.5" style={{ color: T.text3 }}>{p.zone}</p>}
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full font-medium flex-shrink-0"
          style={{ background: statut.bg, color: statut.c }}>
          {statut.label}
        </span>
      </div>

      {/* Type + chef */}
      <div className="flex items-center gap-2 flex-wrap">
        {p.type && (
          <span className="text-[10px] px-2 py-0.5 rounded font-medium capitalize"
            style={{ background: T.canvas, color: T.text3, border: `1px solid ${T.border}` }}>
            {p.type}
          </span>
        )}
        {p.chef_projet && (
          <span className="text-[11px]" style={{ color: T.text3 }}>👤 {p.chef_projet}</span>
        )}
      </div>

      {/* Description */}
      {p.description && (
        <p className="text-xs leading-relaxed" style={{ color: T.text2 }}>
          {p.description.slice(0, 100)}{p.description.length > 100 ? "…" : ""}
        </p>
      )}

      {/* Budget progress */}
      {hasBudget && (
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-[10px]" style={{ color: T.text3 }}>Budget consommé</span>
            <span className="text-[10px] font-mono font-semibold" style={{ color: barColor }}>{pct}%</span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: T.border }}>
            <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: barColor }} />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[10px] font-mono" style={{ color: T.text3 }}>{formatGNF(p.depense_gnf)}</span>
            <span className="text-[10px] font-mono" style={{ color: T.subtle }}>{formatGNF(p.budget_gnf)}</span>
          </div>
        </div>
      )}

      {/* Dates */}
      {(p.date_debut || p.date_fin) && (
        <div className="flex gap-3 pt-1 border-t" style={{ borderColor: T.border }}>
          {p.date_debut && <span className="text-[10px]" style={{ color: T.text3 }}>📅 {formatDate(p.date_debut)}</span>}
          {p.date_fin   && <span className="text-[10px]" style={{ color: T.text3 }}>→ {formatDate(p.date_fin)}</span>}
        </div>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  TERRAIN                                                                ║
// ╚══════════════════════════════════════════════════════════════════════════╝

interface FieldReport {
  id: string; reference: string; technician_phone: string; technician_name: string;
  action: string; location: string; description: string; created_at: string;
}

function actionStyle(a: string) {
  const map: Record<string, { label: string; bg: string; c: string }> = {
    "arrivée":  { label: "Arrivée",  bg: T.accentDim,  c: T.accent   },
    "rapport":  { label: "Rapport",  bg: T.successDim, c: T.success  },
    "départ":   { label: "Départ",   bg: T.surface,    c: T.text3    },
    "incident": { label: "Incident", bg: T.dangerDim,  c: T.danger   },
  };
  return map[a] || { label: a, bg: T.surface, c: T.text3 };
}

function TerrainPanel() {
  const [data, setData] = useState<FieldReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);

  const load = useCallback(async () => {
    const res = await fetch("/api/data/field-reports?today=true");
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 60000); return () => clearInterval(t); }, [load]);

  const interventions = data.filter(r => r.action === "rapport").length;
  const agents        = [...new Set(data.map(r => r.technician_name || r.technician_phone).filter(Boolean))].length;
  const zones         = [...new Set(data.map(r => r.location).filter(Boolean))].length;
  const incidents     = data.filter(r => r.action === "incident").length;

  const display = showAll ? data : data.slice(0, 10);

  return (
    <div className="p-4 md:p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold">Activité terrain</h2>
          <p className="text-xs mt-0.5" style={{ color: T.text3 }}>Rapports d&apos;aujourd&apos;hui — mis à jour chaque minute</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-medium px-2 py-1 rounded-full flex items-center gap-1"
            style={{ background: T.successDim, color: T.success }}>
            <span className="w-1.5 h-1.5 rounded-full inline-block animate-pulse" style={{ background: T.success }}/>
            En direct
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Interventions" value={String(interventions)} color={T.success} />
        <KpiCard label="Agents actifs"  value={String(agents)} />
        <KpiCard label="Zones couvertes" value={String(zones)} />
        <KpiCard label="Incidents"      value={String(incidents)} color={incidents > 0 ? T.danger : T.text3} />
      </div>

      {/* Instructions for technicians */}
      <div className="rounded-xl p-4 mb-6" style={{ background: T.surface, border: `1px solid ${T.border}` }}>
        <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: T.text3 }}>
          Commandes WhatsApp pour les agents terrain
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            { cmd: "arrivée [lieu]",    desc: "Enregistrer une arrivée sur site" },
            { cmd: "rapport [détails]", desc: "Soumettre un rapport d'intervention" },
            { cmd: "départ [lieu]",     desc: "Signaler un départ de site" },
            { cmd: "incident [détails]",desc: "Signaler un incident urgent" },
          ].map(({ cmd, desc }) => (
            <div key={cmd} className="flex items-start gap-3">
              <code className="text-[11px] px-2 py-1 rounded font-mono flex-shrink-0"
                style={{ background: T.canvas, color: T.accent, border: `1px solid ${T.border}` }}>
                {cmd}
              </code>
              <span className="text-[11px] pt-1" style={{ color: T.text3 }}>{desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Activity feed */}
      <DataTable loading={loading}
        empty="Aucun rapport terrain aujourd'hui — les agents envoient via WhatsApp"
        headers={["Heure", "Agent", "Action", "Lieu", "Description"]}
        rows={display.map(r => [
          <span key="t" className="text-[11px] font-mono" style={{ color: T.text3 }}>
            {r.created_at ? new Date(r.created_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }) : "—"}
          </span>,
          <span key="a" className="text-xs">{r.technician_name || r.technician_phone || "—"}</span>,
          <span key="ac" className="text-[10px] px-2 py-0.5 rounded-full font-medium"
            style={{ background: actionStyle(r.action).bg, color: actionStyle(r.action).c }}>
            {actionStyle(r.action).label}
          </span>,
          <span key="l" className="text-xs">{r.location || "—"}</span>,
          <span key="d" className="text-xs" style={{ color: T.text2 }}>
            {(r.description || "").slice(0, 50)}{(r.description || "").length > 50 ? "…" : ""}
          </span>,
        ])}
      />

      {data.length > 10 && (
        <button onClick={() => setShowAll(v => !v)}
          className="w-full mt-4 py-2.5 rounded-lg text-xs font-medium transition-colors"
          style={{ background: T.surface, color: T.text3, border: `1px solid ${T.border}` }}>
          {showAll ? "Voir moins" : `Voir tous les ${data.length} rapports`}
        </button>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  AGENTS                                                                 ║
// ╚══════════════════════════════════════════════════════════════════════════╝

interface AgentLog {
  id: string; agent: string; agent_id: string; icon: string;
  statut: string; insight: string; derniere_execution: string; heure_execution: string;
}

const LOCKED_AGENTS = [
  {
    icon: "📋",
    name: "Agent Facturation",
    tagline: "Facturation automatique",
    description: "Génère les factures automatiquement, envoie les rappels programmés et suit les paiements en temps réel via WhatsApp.",
    benefit: "Réduisez les impayés de 40%",
    price: "£297/mois",
  },
  {
    icon: "📈",
    name: "Agent Rapports",
    tagline: "Rapports & tableaux de bord",
    description: "Rapports mensuels PDF, présentations pour le conseil d'administration et vidéos narratives générés et envoyés automatiquement.",
    benefit: "0 heure de reporting manuel",
    price: "£397/mois",
  },
  {
    icon: "👷",
    name: "Agent Terrain",
    tagline: "Coordination des équipes",
    description: "Dispatch automatique des équipes sur incident, suivi des interventions en temps réel, validation des rapports terrain via WhatsApp.",
    benefit: "Temps de résolution −50%",
    price: "£347/mois",
  },
  {
    icon: "🔮",
    name: "Agent Prédictif",
    tagline: "Maintenance prédictive",
    description: "Analyse les tendances de production pour prédire les pannes, anticiper les pics de demande et optimiser les cycles d'entretien.",
    benefit: "Évitez 80% des pannes imprévues",
    price: "£497/mois",
  },
  {
    icon: "📜",
    name: "Agent Conformité",
    tagline: "Suivi réglementaire",
    description: "Suivi automatique des obligations légales, alertes d'échéances, génération des rapports réglementaires pour les autorités guinéennes.",
    benefit: "Zéro risque de non-conformité",
    price: "£247/mois",
  },
];

function AgentsPanel() {
  const [, setLogs] = useState<AgentLog[]>([]);
  const [stats, setStats] = useState({ messages_today: 0, total_conversations: 0 });
  const [loading, setLoading] = useState(true);
  const [analysing,  setAnalysing]  = useState(false);
  const [generating, setGenerating] = useState(false);
  const [reportUrl,  setReportUrl]  = useState("");
  const [latestInsight, setLatestInsight] = useState<AgentLog | null>(null);
  const [upsellAgent, setUpsellAgent] = useState<typeof LOCKED_AGENTS[0] | null>(null);

  const loadAgents = useCallback(async () => {
    const res = await fetch("/api/data/agents");
    if (res.ok) {
      const data = await res.json();
      setLogs(data.logs || []);
      setStats(data.stats || {});
      const analyseLog = (data.logs as AgentLog[]).find(l => l.agent_id === "data_analyser");
      if (analyseLog) setLatestInsight(analyseLog);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadAgents(); }, [loadAgents]);

  const runAnalysis = async () => {
    setAnalysing(true);
    const res = await fetch("/api/data/agents/analyse", { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      setLatestInsight({ id: data.id, agent: "Agent Analyse", agent_id: "data_analyser", icon: "📊", statut: "actif", insight: data.insight, derniere_execution: "à l'instant", heure_execution: data.heure_execution });
    }
    setAnalysing(false);
  };


  return (
    <div className="p-4 md:p-6 overflow-y-auto">

      {/* Header */}
      <div className="mb-8">
        <h2 className="text-sm font-bold">Agents IA</h2>
        <p className="text-xs mt-0.5" style={{ color: T.text3 }}>
          Votre équipe d'agents travaille en permanence pour vous.
        </p>
      </div>

      {/* ── ACTIVE AGENTS ────────────────────────────────────────────── */}
      <div className="mb-2">
        <p className="text-[10px] font-semibold uppercase tracking-widest mb-4" style={{ color: T.subtle }}>
          Agents actifs
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">

        {/* WhatsApp Agent */}
        <div className="rounded-xl p-5" style={{ background: T.surface, border: `1px solid ${T.border}` }}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                style={{ background: "rgba(37,211,102,.12)" }}>💬</div>
              <div>
                <p className="text-sm font-bold">Agent WhatsApp</p>
                <p className="text-[11px]" style={{ color: T.text3 }}>Service client automatisé</p>
              </div>
            </div>
            <span className="flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-full"
              style={{ background: T.successDim, color: T.success }}>
              <span className="w-1.5 h-1.5 rounded-full inline-block animate-pulse" style={{ background: T.success }} />
              Actif
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4 w-full">
            <div className="rounded-lg p-3" style={{ background: T.canvas }}>
              <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: T.text3 }}>Aujourd'hui</p>
              <p className="text-xl font-bold font-mono">{loading ? "—" : stats.messages_today}</p>
              <p className="text-[10px]" style={{ color: T.text3 }}>messages traités</p>
            </div>
            <div className="rounded-lg p-3" style={{ background: T.canvas }}>
              <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: T.text3 }}>Total</p>
              <p className="text-xl font-bold font-mono">{loading ? "—" : stats.total_conversations}</p>
              <p className="text-[10px]" style={{ color: T.text3 }}>conversations</p>
            </div>
          </div>

          <div className="rounded-lg p-3" style={{ background: T.canvas }}>
            <p className="text-[10px] uppercase tracking-wider mb-1.5" style={{ color: T.text3 }}>Capacités</p>
            {["Répond aux clients en français 24/7", "Qualifie les réclamations et incidents", "Reçoit les rapports terrain des agents", "Briefing quotidien au directeur"].map(c => (
              <div key={c} className="flex items-center gap-2 mb-1">
                <span style={{ color: T.success }}>✓</span>
                <span className="text-[11px]" style={{ color: T.text2 }}>{c}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Data Analyser Agent */}
        <div className="rounded-xl p-5" style={{ background: T.surface, border: `1px solid ${T.border}` }}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                style={{ background: T.accentDim }}>📊</div>
              <div>
                <p className="text-sm font-bold">Agent Analyse</p>
                <p className="text-[11px]" style={{ color: T.text3 }}>Intelligence opérationnelle</p>
              </div>
            </div>
            <span className="flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-full"
              style={{ background: T.successDim, color: T.success }}>
              <span className="w-1.5 h-1.5 rounded-full inline-block animate-pulse" style={{ background: T.success }} />
              Actif
            </span>
          </div>

          {/* Latest insight */}
          <div className="rounded-lg p-4 mb-4 flex-1" style={{ background: T.canvas, minHeight: 120 }}>
            {loading && (
              <div className="space-y-2 animate-pulse">
                <div className="h-3 w-full rounded" style={{ background: T.border }} />
                <div className="h-3 w-4/5 rounded" style={{ background: T.border }} />
                <div className="h-3 w-2/3 rounded" style={{ background: T.border }} />
              </div>
            )}
            {!loading && !latestInsight && (
              <div className="flex flex-col items-center justify-center h-full py-4">
                <p className="text-xs text-center mb-3" style={{ color: T.text3 }}>Aucune analyse générée</p>
                <p className="text-[11px] text-center" style={{ color: T.subtle }}>Cliquez sur Analyser pour obtenir un briefing IA</p>
              </div>
            )}
            {!loading && latestInsight && (
              <>
                <p className="text-xs leading-relaxed whitespace-pre-line" style={{ color: T.text2 }}>
                  {latestInsight.insight}
                </p>
                {latestInsight.heure_execution && (
                  <p className="text-[10px] mt-3" style={{ color: T.subtle }}>
                    Analyse du {new Date(latestInsight.heure_execution).toLocaleString("fr-FR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                  </p>
                )}
              </>
            )}
          </div>

          <button onClick={runAnalysis} disabled={analysing}
            className="w-full py-2.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60"
            style={{ background: T.accent, color: "#fff" }}>
            {analysing ? "Analyse en cours…" : "🔄 Analyser maintenant"}
          </button>

          <button onClick={async () => {
            setGenerating(true);
            const res = await fetch("/api/reports/monthly", {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ manual: true }),
            });
            const data = await res.json();
            if (data.reportUrl) { setReportUrl(data.reportUrl); window.open(data.reportUrl, "_blank"); }
            setGenerating(false);
          }} disabled={generating}
            className="w-full py-2.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60"
            style={{ background: T.canvas, color: T.text2, border: `1px solid ${T.border}` }}>
            {generating ? "Génération en cours…" : "📋 Générer rapport mensuel"}
          </button>

          {reportUrl && (
            <a href={reportUrl} target="_blank" rel="noopener noreferrer"
              className="block text-center text-xs py-2 rounded-lg"
              style={{ background: T.successDim, color: T.success }}>
              ✓ Rapport prêt — Ouvrir
            </a>
          )}
        </div>
      </div>

      {/* ── LOCKED AGENTS ────────────────────────────────────────────── */}
      <div className="mb-4">
        <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color: T.subtle }}>
          Agents disponibles
        </p>
        <p className="text-xs" style={{ color: T.text3 }}>Activez ces agents pour étendre les capacités de votre système.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {LOCKED_AGENTS.map(agent => (
          <div key={agent.name} className="rounded-xl p-5 flex flex-col gap-3 relative overflow-hidden"
            style={{ background: T.surface, border: `1px solid ${T.border}`, opacity: 0.85 }}>

            {/* Lock badge */}
            <span className="absolute top-4 right-4 text-[10px] px-2 py-0.5 rounded-full font-medium"
              style={{ background: T.canvas, color: T.text3, border: `1px solid ${T.border}` }}>
              🔒 Disponible
            </span>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                style={{ background: T.canvas }}>{agent.icon}</div>
              <div>
                <p className="text-sm font-bold">{agent.name}</p>
                <p className="text-[11px]" style={{ color: T.text3 }}>{agent.tagline}</p>
              </div>
            </div>

            <p className="text-xs leading-relaxed" style={{ color: T.text2 }}>{agent.description}</p>

            <div className="rounded-lg px-3 py-2 flex items-center gap-2"
              style={{ background: T.successDim }}>
              <span style={{ color: T.success }}>✦</span>
              <span className="text-[11px] font-medium" style={{ color: T.success }}>{agent.benefit}</span>
            </div>

            <div className="flex items-center justify-between pt-1 mt-auto">
              <span className="text-xs font-mono font-bold" style={{ color: T.text2 }}>{agent.price}</span>
              <button onClick={() => setUpsellAgent(agent)}
                className="text-xs px-4 py-1.5 rounded-lg font-semibold transition-all"
                style={{ background: T.accent, color: "#fff" }}>
                Activer
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Upsell modal */}
      {upsellAgent && (
        <Modal title={upsellAgent.name} onClose={() => setUpsellAgent(null)}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                style={{ background: T.canvas }}>{upsellAgent.icon}</div>
              <div>
                <p className="text-sm font-bold">{upsellAgent.name}</p>
                <p className="text-xs" style={{ color: T.text3 }}>{upsellAgent.tagline}</p>
              </div>
            </div>

            <p className="text-sm leading-relaxed" style={{ color: T.text2 }}>{upsellAgent.description}</p>

            <div className="rounded-lg p-3" style={{ background: T.successDim }}>
              <p className="text-xs font-semibold" style={{ color: T.success }}>✦ {upsellAgent.benefit}</p>
            </div>

            <div className="rounded-lg p-4" style={{ background: T.canvas, border: `1px solid ${T.border}` }}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs" style={{ color: T.text3 }}>Tarif mensuel</span>
                <span className="text-sm font-bold font-mono">{upsellAgent.price}</span>
              </div>
              <p className="text-[11px]" style={{ color: T.subtle }}>Sans engagement · Activable sous 48h</p>
            </div>

            <div className="space-y-2 pt-1">
              <a href={`https://wa.me/447495255315?text=${encodeURIComponent(`Je souhaite activer l'${upsellAgent.name} pour SEGGUINÉE`)}`}
                target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-lg text-sm font-semibold"
                style={{ background: "#25D366", color: "#fff" }}>
                <span>💬</span> Demander l&apos;activation via WhatsApp
              </a>
              <button onClick={() => setUpsellAgent(null)}
                className="w-full py-2.5 rounded-lg text-sm font-medium"
                style={{ background: T.canvas, color: T.text3, border: `1px solid ${T.border}` }}>
                Fermer
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  SHARED COMPONENTS                                                      ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function KpiCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-xl p-5" style={{ background: T.surface, border: `1px solid ${T.border}` }}>
      <p className="text-[11px] uppercase tracking-wider" style={{ color: T.text3 }}>{label}</p>
      <p className="text-2xl font-bold mt-1.5 font-mono" style={{ color: color || T.text }}>{value}</p>
    </div>
  );
}

function DataTable({ headers, rows, loading, empty }: {
  headers: string[]; rows: React.ReactNode[][];
  loading: boolean; empty: string;
}) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: `1px solid ${T.border}` }}>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead style={{ background: T.surface }}>
            <tr>{headers.map((h, i) => (
              <th key={i} className="px-4 py-3 text-[11px] font-medium uppercase tracking-wider" style={{ color: T.text3 }}>{h}</th>
            ))}</tr>
          </thead>
          <tbody>
            {loading && [1,2,3].map(i => (
              <tr key={i} className="animate-pulse" style={{ borderTop: `1px solid ${T.border}` }}>
                {headers.map((_,j) => <td key={j} className="px-4 py-3"><div className="h-4 rounded" style={{ background: T.surface }} /></td>)}
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={headers.length} className="px-4 py-12 text-center text-sm" style={{ color: T.text3 }}>{empty}</td></tr>
            )}
            {!loading && rows.map((row, i) => (
              <tr key={i} style={{ borderTop: `1px solid ${T.border}` }}>
                {row.map((cell, j) => <td key={j} className="px-4 py-3">{cell}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Modal ─────────────────────────────────────────────────────────────────

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="w-full max-w-md rounded-2xl shadow-2xl"
        style={{ background: T.surface, border: `1px solid ${T.border}` }}>
        <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: T.border }}>
          <h3 className="text-sm font-bold">{title}</h3>
          <button onClick={onClose}
            className="w-7 h-7 rounded-md flex items-center justify-center text-lg leading-none transition-colors"
            style={{ background: "transparent", color: T.text3 }}
            onMouseEnter={e => (e.currentTarget.style.background = T.canvas)}
            onMouseLeave={e => (e.currentTarget.style.background = "transparent")}>
            ×
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1.5" style={{ color: T.text2 }}>{label}</label>
      {children}
    </div>
  );
}

function ModalActions({ onCancel, saving, label }: { onCancel: () => void; saving: boolean; label: string }) {
  return (
    <div className="flex gap-3 pt-2">
      <button type="button" onClick={onCancel}
        className="flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors"
        style={{ background: T.canvas, color: T.text3, border: `1px solid ${T.border}` }}>
        Annuler
      </button>
      <button type="submit" disabled={saving}
        className="flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50"
        style={{ background: T.accent, color: "#fff" }}>
        {saving ? "Enregistrement…" : label}
      </button>
    </div>
  );
}

function AddButton({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all"
      style={{ background: T.accent, color: "#fff", boxShadow: "0 2px 8px rgba(59,130,246,.3)" }}
      onMouseEnter={e => (e.currentTarget.style.opacity = "0.9")}
      onMouseLeave={e => (e.currentTarget.style.opacity = "1")}>
      <span className="text-sm leading-none">+</span>
      {children}
    </button>
  );
}

// ── Shared input styles ───────────────────────────────────────────────────

const inputCls = "w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors";
const inputStyle: React.CSSProperties = {
  background: T.canvas,
  border: `1px solid ${T.border}`,
  color: T.text,
};
