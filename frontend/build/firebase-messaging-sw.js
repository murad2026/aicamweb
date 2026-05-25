importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'AIzaSyDH--wYXXXhdEY9G9iLvpOcOITHlUtnayQ',
  authDomain: 'ai-any-camera.firebaseapp.com',
  projectId: 'ai-any-camera',
  storageBucket: 'ai-any-camera.firebasestorage.app',
  messagingSenderId: '256686615559',
  appId: '1:256686615559:web:1dc6fbc34ef017c0eacea2'
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const { title, body } = payload.notification;
  self.registration.showNotification(title, {
    body: body,
    icon: '/logo192.png'
  });
});
