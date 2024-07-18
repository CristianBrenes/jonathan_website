document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.error) {
              document.getElementById('error').textContent = data.error;
          } else {
              document.getElementById('message').textContent = data.message;
              // Add the file ID to the list for downloading
              const fileList = document.getElementById('fileList');
              const fileItem = document.createElement('div');
              fileItem.innerHTML = `<a href="#" onclick="downloadFile('${data.file_id}')">${data.file_id}</a>`;
              fileList.appendChild(fileItem);
          }
      });
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => {
          if (data.access_token) {
              localStorage.setItem('token', data.access_token);
              document.getElementById('message').textContent = 'Login successful';
          } else {
              document.getElementById('error').textContent = data.message;
          }
      });
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('message').textContent = data.message;
      });
});

function downloadFile(file_id) {
    fetch(`/files/${file_id}`, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    }).then(response => response.blob())
      .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = file_id;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
      })
      .catch(error => {
          console.error('Download error:', error);
      });
}