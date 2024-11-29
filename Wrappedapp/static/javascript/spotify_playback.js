window.onSpotifyWebPlaybackSDKReady = () => {
  const token = '[My access token]';
  const player = new Spotify.Player({
    name: 'Web Playback SDK Quick Start Player',
    getOAuthToken: cb => {
      cb(token);
    },
    volume: 0.5
  });
}

player.on('ready', ({ device_id }) => {
    console.log('Ready with Device ID', device_id);
  });

  // Not Ready
  player.on('not_ready', ({ device_id }) => {
    console.log('Device ID has gone offline', device_id);
  });

  player.on('initialization_error', ({ message }) => {
      console.error(message);
  });

  player.on('authentication_error', ({ message }) => {
      console.error(message);
  });

  player.on('account_error', ({ message }) => {
      console.error(message);
  });

    player.connect();
document.getElementById('togglePlay').onclick = function() {
  player.togglePlay();
};