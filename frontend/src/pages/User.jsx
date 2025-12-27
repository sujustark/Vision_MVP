import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { matchFace } from '../api';
import jsQR from 'jsqr';

function User() {
    const { token: urlToken } = useParams();
    const [searchParams] = useSearchParams();
    const tokenFromQuery = searchParams.get('token');

    const [token, setToken] = useState(urlToken || tokenFromQuery || '');
    const [manualToken, setManualToken] = useState('');
    const [qrError, setQrError] = useState(null);
    const [qrSuccess, setQrSuccess] = useState(false);
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (urlToken || tokenFromQuery) {
            setToken(urlToken || tokenFromQuery);
        }
    }, [urlToken, tokenFromQuery]);

    const handleQRUpload = async (e) => {
        if (e.target.files && e.target.files[0]) {
            const qrFile = e.target.files[0];
            setQrError(null);
            setQrSuccess(false);

            // Read the image and decode QR
            const reader = new FileReader();
            reader.onload = (event) => {
                const img = new Image();
                img.onload = () => {
                    // Create canvas to extract image data
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    // Decode QR code
                    const code = jsQR(imageData.data, imageData.width, imageData.height);

                    if (code) {
                        // Extract token from URL
                        const qrUrl = code.data;
                        console.log('QR Code decoded:', qrUrl);

                        // Try to extract token from various URL formats
                        // Format 1: /e/:eventCode/:token
                        // Format 2: ?token=xxx
                        let extractedToken = null;

                        try {
                            const url = new URL(qrUrl);
                            // Check query param
                            if (url.searchParams.get('token')) {
                                extractedToken = url.searchParams.get('token');
                            } else {
                                // Check path segments (e.g., /e/eventCode/token)
                                const pathParts = url.pathname.split('/').filter(Boolean);
                                if (pathParts.length >= 3 && pathParts[0] === 'e') {
                                    extractedToken = pathParts[2];
                                } else if (pathParts.length >= 2) {
                                    // Fallback: use the last path segment as token
                                    extractedToken = pathParts[pathParts.length - 1];
                                }
                            }
                        } catch {
                            // If not a valid URL, treat the whole QR data as token
                            extractedToken = qrUrl;
                        }

                        if (extractedToken) {
                            setManualToken(extractedToken);
                            setQrSuccess(true);
                        } else {
                            setQrError('Could not extract token from QR code');
                        }
                    } else {
                        setQrError('No QR code found in the image. Please try a clearer photo.');
                    }
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(qrFile);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result);
            };
            reader.readAsDataURL(selectedFile);
        }
    };

    const handleMatch = async () => {
        const activeToken = token || manualToken;
        if (!file || !activeToken) {
            setError('Please provide both a token and a selfie.');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const data = await matchFace(activeToken, file);
            if (data.results && data.results.length > 0) {
                setMatches(data.results);
            } else {
                setError('No matches found. Try a different photo or angle.');
            }
        } catch (err) {
            setError('Failed to find matches. Please check your token and try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>Find Your Photos</h1>

            {!token && (
                <div className="token-input-section" style={{ marginBottom: '2rem' }}>
                    <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        Upload a photo of the event QR code:
                    </p>
                    <label htmlFor="qr-upload" style={{
                        display: 'inline-block',
                        padding: '0.75rem 1.5rem',
                        backgroundColor: 'var(--accent)',
                        color: '#0f172a',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 600
                    }}>
                        Choose QR Image
                    </label>
                    <input
                        id="qr-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleQRUpload}
                        style={{ display: 'none' }}
                    />

                    {qrError && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '0.75rem',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid var(--error)',
                            borderRadius: '8px',
                            color: 'var(--error)'
                        }}>
                            {qrError}
                        </div>
                    )}

                    {qrSuccess && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '0.75rem',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            border: '1px solid var(--success)',
                            borderRadius: '8px',
                            color: 'var(--success)'
                        }}>
                            ✓ Token extracted: {manualToken.substring(0, 15)}...
                        </div>
                    )}
                </div>
            )}

            {token && (
                <div style={{
                    padding: '0.75rem',
                    backgroundColor: '#e8f5e9',
                    borderRadius: '8px',
                    marginBottom: '1.5rem',
                    border: '1px solid #4caf50'
                }}>
                    <p style={{ margin: 0, color: '#2e7d32' }}>
                        ✓ Event token loaded: {token.substring(0, 10)}...
                    </p>
                </div>
            )}

            <div className="upload-section" style={{ marginBottom: '2rem' }}>
                <p style={{ marginBottom: '1rem', color: '#666' }}>Upload a selfie to find your photos:</p>

                <label htmlFor="file-upload" style={{
                    display: 'inline-block',
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#2196f3',
                    color: 'white',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    marginBottom: '1rem'
                }}>
                    Choose Photo
                </label>
                <input
                    id="file-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                />

                {preview && (
                    <div style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                        <img
                            src={preview}
                            alt="Preview"
                            style={{
                                maxWidth: '200px',
                                maxHeight: '200px',
                                borderRadius: '8px',
                                border: '2px solid #e0e0e0'
                            }}
                        />
                    </div>
                )}

                <button
                    onClick={handleMatch}
                    disabled={!file || (!token && !manualToken) || loading}
                    style={{
                        padding: '0.75rem 2rem',
                        fontSize: '1rem',
                        backgroundColor: (!file || (!token && !manualToken) || loading) ? '#ccc' : '#4caf50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: (!file || (!token && !manualToken) || loading) ? 'not-allowed' : 'pointer',
                        marginTop: '1rem'
                    }}
                >
                    {loading ? 'Searching...' : 'Find My Photos'}
                </button>
            </div>

            {error && (
                <div style={{
                    padding: '1rem',
                    backgroundColor: '#ffebee',
                    color: '#c62828',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    border: '1px solid #ef5350'
                }}>
                    {error}
                </div>
            )}

            {matches.length > 0 && (
                <div>
                    <h2 style={{ marginBottom: '1rem' }}>Found {matches.length} photo{matches.length > 1 ? 's' : ''}!</h2>
                    <div className="results-grid" style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                        gap: '1.5rem',
                        marginTop: '1.5rem'
                    }}>
                        {matches.map((match, index) => (
                            <div key={index} className="photo-card" style={{
                                border: '2px solid #e0e0e0',
                                borderRadius: '12px',
                                overflow: 'hidden',
                                backgroundColor: 'white',
                                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                            }}>
                                <div style={{
                                    width: '100%',
                                    height: '250px',
                                    overflow: 'hidden',
                                    backgroundColor: '#f5f5f5'
                                }}>
                                    <img
                                        src={`/api/v1/images?path=${encodeURIComponent(match.image_path)}`}
                                        alt="Matched"
                                        style={{
                                            width: '100%',
                                            height: '100%',
                                            objectFit: 'cover'
                                        }}
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            e.target.parentElement.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#999;">Image not available</div>';
                                        }}
                                    />
                                </div>
                                <div style={{
                                    padding: '0.75rem',
                                    backgroundColor: '#f9f9f9',
                                    borderTop: '1px solid #e0e0e0'
                                }}>
                                    <span style={{ fontSize: '0.9rem', color: '#666' }}>
                                        Match Score: {(match.score * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!loading && !error && file && matches.length === 0 && (token || manualToken) && (
                <div style={{
                    padding: '1rem',
                    backgroundColor: '#fff3e0',
                    borderRadius: '8px',
                    border: '1px solid #ff9800',
                    color: '#e65100'
                }}>
                    No matches found yet. Try uploading a different photo or check if the event has been indexed.
                </div>
            )}
        </div>
    );
}

export default User;
