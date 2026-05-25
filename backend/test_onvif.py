from onvif_scanner import probe_onvif
for user in ['root', 'admin']:
    for pwd in ['Mered123$', 'admin', '12345', '']:
        r = probe_onvif('192.168.3.105', 80, user, pwd)
        if r:
            print('Found:', user, pwd, r)
            break
