import { Link } from "react-router-dom";
export default function Privacy() {
  return <main className="legal-page"><div className="legal-wrap"><Link to="/" className="legal-brand">← N1MOX30</Link><span className="auth-kicker">LEGAL</span><h1>Privacy Policy</h1><p className="legal-updated">Draft product policy · Last updated September 2026</p>
    <section><h2>1. Information we process</h2><p>Depending on the features you use, N1MOX30 may process account information, workflow data, creator content, analytics, connected-platform identifiers and technical information needed to operate the service.</p></section>
    <section><h2>2. How information is used</h2><p>Information may be used to authenticate users, execute workflows, generate content, provide analytics, schedule actions, improve reliability and provide support.</p></section>
    <section><h2>3. Connected accounts</h2><p>When you connect a third-party account, N1MOX30 processes the permissions and data made available through that integration. You can disconnect supported accounts through the product.</p></section>
    <section><h2>4. AI providers</h2><p>Some features may route prompts or content through configured AI providers. The exact provider and retention behavior depends on the provider configuration and applicable terms.</p></section>
    <section><h2>5. Security</h2><p>N1MOX30 is designed to use authentication, access controls and secure handling practices. No internet service can guarantee absolute security.</p></section>
    <section><h2>6. Retention</h2><p>Data may be retained as necessary to provide the service, maintain workflows, meet operational requirements and comply with legal obligations. Specific retention periods should be defined before commercial launch.</p></section>
    <section><h2>7. Your choices</h2><p>Subject to applicable law and product capabilities, you may request access, correction or deletion of personal information and may disconnect integrations.</p></section>
    <section><h2>8. Updates</h2><p>This policy may change as N1MOX30 adds features and integrations. The effective version should be presented through the product.</p></section>
    <div className="legal-warning">This is a product-ready draft template, not legal advice. Have qualified counsel review it for applicable Indian and international privacy requirements before commercial launch.</div>
  </div></main>;
}
