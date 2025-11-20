import React, { useState } from 'react';
import { registerEvent } from '../api';
import QRCode from 'react-qr-code';

function Studio() {
    const [storagePath, setStoragePath] = useState('');
    const [eventData, setEventData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const data = await registerEvent(storagePath);
            setEventData(data);
        } catch (err) {
            setError('Failed to register event. Please check the path and try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>Studio Portal</h1>
            <p>Enter the path to your photo storage to generate a QR code for your event.</p>

            <form onSubmit={handleSubmit} className="studio-form">
                <input
                    type="text"
                    placeholder="e.g. D:\Photos\Event1"
                    value={storagePath}
                    onChange={(e) => setStoragePath(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : 'Generate QR'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            {eventData && (
                <div className="result-section">
                    <h2>Event Registered!</h2>
                    <div className="qr-code">
                        <QRCode value={eventData.qr_link} />
                    </div>
                    <p>Scan this QR code to find your photos.</p>
                    <div className="event-details">
                        <p><strong>Event Code:</strong> {eventData.event_code}</p>
                        <p><strong>Token:</strong> {eventData.token}</p>
                        <p><strong>Link:</strong> <a href={eventData.qr_link} target="_blank" rel="noreferrer">{eventData.qr_link}</a></p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Studio;
