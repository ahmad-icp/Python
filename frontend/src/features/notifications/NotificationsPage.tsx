import { useEffect, useState } from 'react';
import { listNotifications, listNotificationTemplates, NotificationItem, processNotificationQueue, TemplateItem } from '../../services/notifications';

export function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = () => Promise.all([listNotifications(), listNotificationTemplates()]).then(([notifications, loadedTemplates]) => { setItems(notifications.items); setTemplates(loadedTemplates); });
  useEffect(() => { load().catch((e) => setError(e.message)); }, []);
  const processQueue = async () => { try { const result = await processNotificationQueue(); setMessage(`Processed ${result.processed}, sent ${result.sent}, failed ${result.failed}`); await load(); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to process queue'); } };
  return <section style={{ marginTop: '2rem' }}>
    <h2>Notification Center</h2>
    <p>Email, SMS, WhatsApp, push-ready and in-app notification queue with delivery tracking.</p>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
    {message && <p role="status" style={{ color: 'green' }}>{message}</p>}
    <button type="button" onClick={processQueue}>Process Queue</button>
    <h3>Templates ({templates.length})</h3>
    <ul>{templates.map((template) => <li key={template.id}>{template.name} · {template.channel} · {template.event_type}</li>)}</ul>
    <h3>Recent Notifications</h3>
    <ul>{items.map((item) => <li key={item.id}>{item.channel} to {item.recipient_type}:{item.recipient_id} — {item.status}</li>)}</ul>
  </section>;
}
