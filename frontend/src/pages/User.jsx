import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { matchFace } from '../api';

function User() {
    const { eventCode, token: urlToken } = useParams();
    const [searchParams] = useSearchParams();
    const tokenFromQuery = searchParams.get('token');

    const [token, setToken] = useState(urlToken || tokenFromQuery || '');
    const [manualToken, setManualToken] = useState('');
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
                    <p>Enter your event token:</p>
                    <input
                        type="text"
                        placeholder="Event Token (e.g., R6GEyBfhhD_u0PFSGmjA9g)"
                        value={manualToken}
                        onChange={(e) => setManualToken(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            marginBottom: '1rem',
                            border: '2px solid #e0e0e0',
                            borderRadius: '8px',
                            fontSize: '1rem'
                        }}
                    />
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
                                        src={`http://localhost:8000/api/v1/images?path=${encodeURIComponent(match.image_path)}`}
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
