"use client";

/**
 * Dashboard — SEGGUINÉE Operations Portal
 * Tabs: Conversations | Production | Factures | Incidents
 * SEGGUINÉE Navy dark mode (§14.8 preset)
 */

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

// ── Types ──────────────────────────────────────────────────────────────────

interface Conversation {
  id: string;
  phone: string;
  profile_name: string;
  last_message: string;
  last_message_at: string;
  unread_count: number;
  status: string;
  is_director: boolean;
}
interface Message {
  id: string;
  conversation_id: string;
  direction: "inbound" | "outbound";
  body: string;
  action: string;
  ai_generated: boolean;
  read: boolean;
  created_at: string;
}
interface ProductionEntry {
  id: string;
  volume_m3: number;
  station: string;
  zone: string;
  recorded_by: string;
  recorded_at: string;
}
interface Invoice {
  id: string;
  customer_phone: string;
  customer_name: string;
  amount_gnf: number;
  reference: string;
  due_date: string;
  status: "pending" | "paid" | "overdue" | "cancelled";
  paid_at: string | null;
  created_at: string;
}
interface Incident {
  id: string;
  type: string;
  description: string;
  zone: string;
  station: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  reported_by: string;
  created_at: string;
}

type Tab = "conversations" | "production" | "invoices" | "incidents";

// ── Design tokens (§14.8 SEGGUINÉE Navy) ────────────────────────────────────

const T = {
  canvas: "#0F172A",
  surface: "#1E293B",
  surfaceHover: "#273449",
  border: "#334155",
  accent: "#3B82F6",
  accentDim: "rgba(59,130,246,.15)",
  text: "#F8FAFC",
  text2: "#CBD5E1",
  text3: "#94A3B8",
  subtle: "#64748B",
  success: "#34D399",
  successDim: "rgba(52,211,153,.15)",
  warning: "#FBBF24",
  warningDim: "rgba(251,191,36,.15)",
  danger: "#F87171",
  dangerDim: "rgba(248,113,113,.15)",
};

// ── Status helpers ──────────────────────────────────────────────────────────

function invoiceStatusBadge(s: string) {
  const map: Record<string, { label: string; bg: string; c: string }> = {
    pending: { label: "En attente", bg: T.warningDim, c: T.warning },
    paid: { label: "Payée", bg: T.successDim, c: T.success },
    overdue: { label: "En retard", bg: T.dangerDim, c: T.danger },
    cancelled: { label: "Annulée", bg: T.surface, c: T.text3 },
  };
  const b = map[s] || map.pending;
  return (
    <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: b.bg, color: b.c }}>
      {b.label}
    </span>
  );
}

function incidentStatusBadge(s: string) {
  const map: Record<string, { label: string; bg: string; c: string }> = {
    open: { label: "Ouvert", bg: T.dangerDim, c: T.danger },
    in_progress: { label: "En cours", bg: T.warningDim, c: T.warning },
    resolved: { label: "Résolu", bg: T.successDim, c: T.success },
    closed: { label: "Fermé", bg: T.surface, c: T.text3 },
  };
  const b = map[s] || map.open;
  return (
    <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: b.bg, color: b.c }}>
      {b.label}
    </span>
  );
}

function formatTime(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  return d.toDateString() === now.toDateString()
    ? d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
    : d.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
}

function formatDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}

function formatGNF(n: number): string {
  return n.toLocaleString("fr-FR") + " GNF";
}

// ── Tab definitions ────────────────────────────────────────────────────────

const tabs: { key: Tab; label: string; icon: string }[] = [
  { key: "conversations", label: "Conversations", icon: "💬" },
  { key: "production", label: "Production", icon: "📊" },
  { key: "invoices", label: "Factures", icon: "📄" },
  { key: "incidents", label: "Incidents", icon: "🚨" },
];

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  DASHBOARD PAGE                                                         ║
// ╚══════════════════════════════════════════════════════════════════════════╝

export default function DashboardPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("conversations");
  const [session, setSession] = useState<any>(null);

  // Auth check — accept PIN cookie OR Supabase session OR sessionStorage
  useEffect(() => {
    const hasPinCookie = document.cookie.includes("segguinee_auth=");
    if (hasPinCookie) {
      setSession({ provider: "pin" } as any);
      return;
    }
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session && !sessionStorage.getItem("segguinee_auth")) {
        router.push("/login");
        return;
      }
      setSession(session);
    });
  }, [router]);

  const handleLogout = async () => {
    sessionStorage.removeItem("segguinee_auth");
    document.cookie = "segguinee_auth=; path=/; max-age=0";
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <div className="h-screen flex flex-col" style={{ background: T.canvas, color: T.text }}>
      {/* ── Top Bar ──────────────────────────────────────────────────────── */}
      <header className="flex-shrink-0 border-b px-6 py-3 flex items-center justify-between" style={{ borderColor: T.border, background: T.surface }}>
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-sm font-bold tracking-tight">SEGGUINÉE</h1>
            <p className="text-[11px]" style={{ color: T.subtle }}>Portail Opérateur</p>
          </div>
          {/* Tab navigation */}
          <nav className="flex gap-1 ml-6">
            {tabs.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                className="px-4 py-2 text-xs font-medium rounded-md transition-colors"
                style={{
                  background: tab === t.key ? T.canvas : "transparent",
                  color: tab === t.key ? T.accent : T.text3,
                }}
              >
                <span className="mr-1.5">{t.icon}</span>
                {t.label}
              </button>
            ))}
          </nav>
        </div>
        <button
          onClick={handleLogout}
          className="text-xs px-3 py-1.5 rounded-md transition-colors"
          style={{ background: T.canvas, color: T.text3 }}
        >
          Déconnexion
        </button>
      </header>

      {/* ── Panel Content ────────────────────────────────────────────────── */}
      <div className="flex-1 min-h-0">
        {tab === "conversations" && <ConversationsPanel />}
        {tab === "production" && <ProductionPanel />}
        {tab === "invoices" && <InvoicesPanel />}
        {tab === "incidents" && <IncidentsPanel />}
      </div>
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  CONVERSATIONS PANEL                                                    ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function ConversationsPanel() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = useCallback(async () => {
    const { data } = await supabase
      .from("conversations")
      .select("*")
      .order("last_message_at", { ascending: false });
    if (data) setConversations(data);
    setLoading(false);
  }, []);

  useEffect(() => { loadConversations(); }, [loadConversations]);

  // Real-time
  useEffect(() => {
    const ch = supabase
      .channel("conversations")
      .on("postgres_changes", { event: "*", schema: "public", table: "conversations" }, () => loadConversations())
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [loadConversations]);

  // Messages for selected
  useEffect(() => {
    if (!selectedId) return;
    supabase.from("messages").select("*").eq("conversation_id", selectedId).order("created_at", { ascending: true })
      .then(({ data }) => { if (data) setMessages(data); });
    supabase.from("conversations").update({ unread_count: 0 }).eq("id", selectedId).then(() => loadConversations());
    const msgCh = supabase
      .channel(`msgs:${selectedId}`)
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "messages", filter: `conversation_id=eq.${selectedId}` },
        (payload) => setMessages((prev) => [...prev, payload.new as Message]))
      .subscribe();
    return () => { supabase.removeChannel(msgCh); };
  }, [selectedId, loadConversations]);

  const selected = conversations.find((c) => c.id === selectedId);

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="w-80 lg:w-96 flex-shrink-0 border-r flex flex-col" style={{ borderColor: T.border }}>
        <div className="flex-1 overflow-y-auto">
          {loading && [1, 2, 3].map((i) => (
            <div key={i} className="p-4 animate-pulse border-b" style={{ borderColor: T.border }}>
              <div className="h-4 w-2/3 rounded mb-2" style={{ background: T.surface }} />
              <div className="h-3 w-full rounded" style={{ background: T.surface }} />
            </div>
          ))}
          {!loading && conversations.length === 0 && (
            <div className="p-8 text-center"><p style={{ color: T.text3 }}>Aucune conversation</p></div>
          )}
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedId(c.id)}
              className="w-full text-left p-4 border-b transition-colors"
              style={{ background: selectedId === c.id ? T.surface : T.canvas, borderColor: T.border }}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium truncate">{c.profile_name || c.phone}</span>
                    {c.is_director && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full font-medium" style={{ background: T.accentDim, color: T.accent }}>Directeur</span>
                    )}
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

      {/* Message thread */}
      <main className="flex-1 flex flex-col min-w-0">
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
                <p className="text-xs" style={{ color: T.text3, fontFamily: "'JetBrains Mono', monospace" }}>{selected.phone}</p>
              </div>
              {selected.is_director && <span className="text-xs px-3 py-1 rounded-full font-medium" style={{ background: T.accentDim, color: T.accent }}>Directeur</span>}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m) => (
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
// ║  PRODUCTION PANEL                                                       ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function ProductionPanel() {
  const [data, setData] = useState<ProductionEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const { data } = await supabase
      .from("production")
      .select("*")
      .order("recorded_at", { ascending: false })
      .limit(50);
    if (data) setData(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const ch = supabase
      .channel("production")
      .on("postgres_changes", { event: "*", schema: "public", table: "production" }, () => load())
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [load]);

  const totalM3 = data.reduce((s, e) => s + (e.volume_m3 || 0), 0);

  return (
    <div className="p-6 h-full overflow-y-auto">
      {/* KPI row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <KpiCard label="Volume Total (m³)" value={totalM3.toLocaleString("fr-FR")} />
        <KpiCard label="Stations Actives" value={String(new Set(data.map((d) => d.station).filter(Boolean)).size)} />
        <KpiCard label="Relevés Aujourd'hui" value={String(data.filter((d) => new Date(d.recorded_at).toDateString() === new Date().toDateString()).length)} />
      </div>

      {/* Table */}
      <DataTable
        loading={loading}
        empty="Aucune donnée de production"
        headers={["Volume (m³)", "Station", "Zone", "Date", "Enregistré par"]}
        rows={data.map((d) => [
          <span key="v" className="font-mono font-semibold">{d.volume_m3.toLocaleString("fr-FR")}</span>,
          d.station || "—",
          d.zone || "—",
          <span key="d" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.recorded_at)}</span>,
          <span key="b" className="text-[11px] font-mono" style={{ color: T.text3 }}>{d.recorded_by || "—"}</span>,
        ])}
      />
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  INVOICES PANEL                                                         ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function InvoicesPanel() {
  const [data, setData] = useState<Invoice[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    let q = supabase.from("invoices").select("*").order("created_at", { ascending: false }).limit(100);
    if (filter !== "all") q = q.eq("status", filter);
    const { data } = await q;
    if (data) setData(data);
    setLoading(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const ch = supabase
      .channel("invoices")
      .on("postgres_changes", { event: "*", schema: "public", table: "invoices" }, () => load())
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [load]);

  const pending = data.filter((i) => i.status === "pending").reduce((s, i) => s + i.amount_gnf, 0);
  const paid = data.filter((i) => i.status === "paid").reduce((s, i) => s + i.amount_gnf, 0);

  return (
    <div className="p-6 h-full overflow-y-auto">
      {/* KPI row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <KpiCard label="En Attente (GNF)" value={formatGNF(pending)} color={T.warning} />
        <KpiCard label="Payé (GNF)" value={formatGNF(paid)} color={T.success} />
        <KpiCard label="Total Factures" value={String(data.length)} />
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {[
          { k: "all", l: "Toutes" },
          { k: "pending", l: "En attente" },
          { k: "paid", l: "Payées" },
          { k: "overdue", l: "En retard" },
        ].map((f) => (
          <button
            key={f.k}
            onClick={() => { setFilter(f.k); setLoading(true); }}
            className="text-xs px-3 py-1.5 rounded-md transition-colors"
            style={{ background: filter === f.k ? T.accent : T.surface, color: filter === f.k ? T.text : T.text3 }}
          >
            {f.l}
          </button>
        ))}
      </div>

      {/* Table */}
      <DataTable
        loading={loading}
        empty="Aucune facture"
        headers={["Référence", "Client", "Montant", "Échéance", "Statut"]}
        rows={data.map((d) => [
          <span key="r" className="font-mono text-[11px]">{d.reference || "—"}</span>,
          <span key="c" className="text-xs">{d.customer_phone || d.customer_name || "—"}</span>,
          <span key="m" className="font-mono font-semibold">{d.amount_gnf.toLocaleString("fr-FR")} GNF</span>,
          <span key="e" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.due_date)}</span>,
          invoiceStatusBadge(d.status),
        ])}
      />
    </div>
  );
}

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  INCIDENTS PANEL                                                        ║
// ╚══════════════════════════════════════════════════════════════════════════╝

function IncidentsPanel() {
  const [data, setData] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const { data } = await supabase
      .from("incidents")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50);
    if (data) setData(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const ch = supabase
      .channel("incidents")
      .on("postgres_changes", { event: "*", schema: "public", table: "incidents" }, () => load())
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [load]);

  const active = data.filter((i) => i.status === "open" || i.status === "in_progress").length;

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="grid grid-cols-3 gap-4 mb-6">
        <KpiCard label="Incidents Actifs" value={String(active)} color={active > 0 ? T.danger : T.success} />
        <KpiCard label="Total Signalés" value={String(data.length)} />
        <KpiCard label="Résolus" value={String(data.filter((i) => i.status === "resolved" || i.status === "closed").length)} color={T.success} />
      </div>

      <DataTable
        loading={loading}
        empty="Aucun incident signalé"
        headers={["Type", "Description", "Zone", "Date", "Statut"]}
        rows={data.map((d) => [
          <span key="t" className="text-xs font-medium capitalize">{d.type || "—"}</span>,
          <span key="d" className="text-xs">{d.description.slice(0, 60)}{d.description.length > 60 ? "…" : ""}</span>,
          <span key="z" className="text-xs">{d.zone || d.station || "—"}</span>,
          <span key="dt" className="text-[11px]" style={{ color: T.text3 }}>{formatDate(d.created_at)}</span>,
          incidentStatusBadge(d.status),
        ])}
      />
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

function DataTable({
  headers, rows, loading, empty,
}: {
  headers: string[];
  rows: React.ReactNode[][];
  loading: boolean;
  empty: string;
}) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: `1px solid ${T.border}` }}>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead style={{ background: T.surface }}>
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="px-4 py-3 text-[11px] font-medium uppercase tracking-wider" style={{ color: T.text3 }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && [1, 2, 3].map((i) => (
              <tr key={i} className="animate-pulse" style={{ borderTop: `1px solid ${T.border}` }}>
                {headers.map((_, j) => (
                  <td key={j} className="px-4 py-3"><div className="h-4 rounded" style={{ background: T.surface }} /></td>
                ))}
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={headers.length} className="px-4 py-12 text-center" style={{ color: T.text3 }}>
                  {empty}
                </td>
              </tr>
            )}
            {!loading && rows.map((row, i) => (
              <tr key={i} style={{ borderTop: `1px solid ${T.border}` }}>
                {row.map((cell, j) => (
                  <td key={j} className="px-4 py-3">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
