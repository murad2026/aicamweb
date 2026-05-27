export async function requestPushPermission() {
  try {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  } catch(e) {
    return false;
  }
}

export function showNotification(title, body) {
  if (Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/logo192.png' });
  }
}
