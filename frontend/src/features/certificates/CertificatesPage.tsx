import { useEffect, useState } from 'react';
import { CertificateRequest, DocumentItem, listCertificateRequests, listDocuments } from '../../services/certificates';

export function CertificatesPage() {
  const [certificates, setCertificates] = useState<CertificateRequest[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { Promise.all([listCertificateRequests(), listDocuments()]).then(([certificateResponse, loadedDocuments]) => { setCertificates(certificateResponse.items); setDocuments(loadedDocuments); }).catch((e) => setError(e.message)); }, []);
  return <section style={{ marginTop: '2rem' }}>
    <h2>Certificate & Document Management</h2>
    <p>Certificates, QR verification, document repository, and approval workflows.</p>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
    <h3>Certificate Requests</h3>
    <ul>{certificates.map((certificate) => <li key={certificate.id}>{certificate.certificate_type} · {certificate.status} · {certificate.verification_code}</li>)}</ul>
    <h3>Document Repository</h3>
    <ul>{documents.map((document) => <li key={document.id}>{document.title} · {document.owner_type}:{document.owner_id} · {document.approval_status}</li>)}</ul>
  </section>;
}
