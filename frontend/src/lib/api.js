// Tiny helper for calling the Flask JSON API.
// credentials:"same-origin" makes the browser send your login cookie, so the
// server knows who you are. If the session has expired (401), we send the
// user back to the Flask login page.
export async function getJSON(path) {
  const res = await fetch(path, { credentials: 'same-origin' })
  if (res.status === 401) {
    window.location.href = '/login'
    throw new Error('unauthorized')
  }
  if (!res.ok) throw new Error('request failed: ' + res.status)
  return res.json()
}
