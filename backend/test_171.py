from onvif_scanner import probe_onvif
for user in ['admin', 'root']:
    r = probe_onvif('192.168.3.171', 80, user, 'Mered123$')
    if r:
        print('Found:', user, r)
