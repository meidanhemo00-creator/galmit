// POST /api/contact  ->  sends the site's contact form by SMTP.
// Env (set in Vercel): SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
// Optional: CONTACT_TO (default bags@pashutyarok.co.il), SMTP_FROM (default SMTP_USER)
import nodemailer from 'nodemailer';

const clean = (v, max) => String(v ?? '').replace(/[\r\n]+/g, ' ').trim().slice(0, max);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'method' });
  }
  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
    return res.status(503).json({ ok: false, error: 'not_configured' });
  }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
  body ||= {};
  if (body._honey) return res.status(200).json({ ok: true }); // bot

  const name = clean(body.name, 120);
  const phone = clean(body.phone, 40);
  const company = clean(body.company, 160);
  const message = String(body.message ?? '').trim().slice(0, 3000);
  const digits = phone.replace(/\D/g, '');
  if (name.length < 2 || digits.length < 9 || digits.length > 12) {
    return res.status(400).json({ ok: false, error: 'invalid' });
  }

  const port = Number(SMTP_PORT) || 465;
  const transport = nodemailer.createTransport({
    host: SMTP_HOST, port, secure: port === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
    connectionTimeout: 10000, greetingTimeout: 10000, socketTimeout: 15000
  });

  const rows = [['שם', name], ['טלפון', phone], ['חברה', company || '-'], ['מה אורזים', message || '-']];
  const text = rows.map(([k, v]) => `${k}: ${v}`).join('\n');
  const html = `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:15px">
<p>פנייה חדשה מהאתר galmit.co.il</p>
<table cellpadding="8" style="border-collapse:collapse">${rows.map(([k, v]) =>
    `<tr><td style="border:1px solid #ddd;font-weight:bold">${k}</td><td style="border:1px solid #ddd;white-space:pre-wrap">${esc(v)}</td></tr>`).join('')}
</table>
<p><a href="tel:${digits}">להתקשר</a> · <a href="https://wa.me/972${digits.replace(/^0/, '')}">וואטסאפ</a></p></div>`;

  try {
    await transport.sendMail({
      from: { name: 'אתר גלמית', address: process.env.SMTP_FROM || SMTP_USER },
      to: process.env.CONTACT_TO || 'bags@pashutyarok.co.il',
      subject: `פנייה מהאתר: ${name}${company ? ` · ${company}` : ''}`,
      text, html
    });
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('contact smtp error:', err && err.message);
    return res.status(502).json({ ok: false, error: 'send_failed' });
  }
}
