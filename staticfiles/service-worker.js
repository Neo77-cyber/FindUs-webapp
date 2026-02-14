// IMPROVED SIMPLE SERVICE WORKER
self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        // Return a nicer offline page
        return new Response(`
          <!DOCTYPE html>
          <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Offline - FindUs</title>
            <style>
              body {
                font-family: -apple-system, sans-serif;
                background: #077f46;
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 20px;
              }
              h1 { font-size: 28px; margin-bottom: 20px; }
              p { font-size: 18px; margin-bottom: 30px; }
              button {
                background: white;
                color: #077f46;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
              }
            </style>
          </head>
          <body>
            <h1>📶 You're Offline</h1>
            <p>Please check your internet connection.</p>
            <button onclick="window.location.reload()">Try Again</button>
            <script>
              window.addEventListener('online', () => {
                window.location.reload();
              });
            </script>
          </body>
          </html>
        `, { headers: {'Content-Type': 'text/html'} });
      })
    );
  }
});