import os

soundwave_ip = '127.0.0.1'
target_ip = '127.0.0.1'
ADAPTER = 'lo'


# Configure settings on initial import
def set_soundwave_ip():
    global soundwave_ip
    result = ''.join(os.popen('ifconfig').readlines())
    result_arr = result.split(': flags')
    for i in range(len(result_arr) - 1):
        if i == 0:
            name = result_arr[i]
        else:
            name = result_arr[i].split('\n')[-1]

        ip = result_arr[i + 1].split('inet ')[1].split(' ')[0]

        if name == ADAPTER:
            soundwave_ip = ip
            print(f'Set Soundwave IP to {ip}')
            return
    print('Could not set Soundwave IP, check adapters')
    exit(-1)


set_soundwave_ip()
