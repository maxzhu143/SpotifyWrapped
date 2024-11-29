const token =  "{{ access_token }}";

async function fetchWebApi(endpoint, method, body) {
  const res = await fetch(`https://api.spotify.com/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    method,
    body: JSON.stringify(body),
  });
  return await res.json();
}

async function getTopTracks() {
  return (await fetchWebApi(
    'v1/me/top/tracks?time_range=long_term&limit=5', 'GET'
  )).items;
}

document.addEventListener("DOMContentLoaded", async () => {
  const topTracks = await getTopTracks();
  console.log(
    topTracks?.map(
      ({name, artists}) =>
        `${name} by ${artists.map(artist => artist.name).join(', ')}`
    )
  );
});
async function fetchTopTracksAndDescribe(token) {
  try {
    // Fetch the user's top tracks
    const topTracks = await getTopTracks();

    // Extract track names for the prompt
    const trackNames = topTracks.map(track => track.name);

    // Send the track names to the Django backend
    const response = await fetch('/describe-user-tracks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),  // CSRF protection if needed
      },
      body: JSON.stringify({ trackNames })
    });

    const data = await response.json();
    if (data.description) {
      // Display the description
      document.getElementById('userDescription').innerText = data.description;
    }
  } catch (error) {
    console.error("Error fetching or sending top tracks:", error);
  }
}

// Helper function for CSRF token
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

