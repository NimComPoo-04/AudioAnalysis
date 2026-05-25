const buttons = {
    'start-recording': undefined,
    'stop-recording': undefined,
}

const recorded_audios = { }

const conn_status = document.querySelector('.control-status-nope')

const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
        sampleRate: 16000,
        noiseSuppression: true
    },
    video: false
})
const recorder = new MediaRecorder(stream);

const table = document.querySelector('.audio-body table')

recorder.addEventListener('dataavailable', function(eve) {
    const blb = new Blob([eve.data], {type: recorder.mimeType})

    const time= new Date().getTime()

    const row = document.createElement('tr')
    row.id = `row-${time}`
    row.innerHTML = `<td>${time}</td>
        <td id=audio-${time}></td>
        <td><button id=operator-${time}>Analyse</button></td>`

    const where_to_add = table.querySelector('tbody')
    where_to_add.appendChild(row)

    const audio = document.createElement("audio");
    audio.controls = true;
    const audioURL = URL.createObjectURL(blb)
    audio.src = audioURL
    audio.addEventListener('load', () => {
        URL.revokeObjectURL(audioURL)
    })

    document.getElementById(`audio-${time}`).appendChild(audio)

    const op = document.getElementById(`operator-${time}`)
    recorded_audios[time] = {
        'timestamp': time,
        'audio': audio,
        'operator': op
    }

    op.addEventListener('click', async (e) => {

        const fd= new FormData()
        fd.append('file', blb, "rotund.mp3")

        const analysis = await fetch('/recognize', {
            method: 'POST',
            body: fd,
            mode: 'cors'
        })

        const foobar = await analysis.json()
        const results = foobar['result']

        const results_table = document.querySelector('.results-body table tbody')
        results_table.innerHTML = ''

        const keys = Object.keys(results['time'])

        const summary_judgement = {
            'car': 0,
            'truck': 0,
            'bus': 0,
            'unknown': 0
        }

        for(const key of keys) {
            const time = results['time'][key]
            const guess1 = results['guess 1'][key]
            const guess2 = results['guess 2'][key]
            const guess3 = results['guess 3'][key]
            const guess4 = results['guess 4'][key]
            const guess5 = results['guess 5'][key]
            const confidence = parseInt(results['confidence'][key] * 100)
            const classes = results['classes'][key]
            const anchor = results['anchor_horn'][key]

            let horn_qq = false
            if(classes == 'Nope') { // not a horn at all
                horn_qq = false
            }
            else if(classes.search('|') > 0) {   // shit has a vehicle type
                horn_qq = confidence > 60

                if(horn_qq) {
                    const ree = classes.split('|')[1].trim().toLowerCase()

                    if(summary_judgement[ree])
                        summary_judgement[ree] += 1
                    else
                        summary_judgement[ree] = 1
                }
            }
            else { // maybe a horn
                horn_qq = confidence > 80
                summary_judgement['unknown'] += 1
            }

            const tr = document.createElement('tr')

            if(horn_qq)
                tr.style = 'background: yellowgreen;'
            else if( classes.search('|') > 0 )
                tr.style = 'background: yellow;'

            tr.innerHTML = `<td>${time}</td>
                            <td>${guess1}</td>
                            <td>${guess2}</td>
                            <td>${guess3}</td>
                            <td>${guess4}</td>
                            <td>${guess5}</td>
                            <td>${classes}</td>
                            <td>${confidence}</td>
                            <td>${anchor}</td>
                            <td>${horn_qq ? 'Yes' : 'No'}</td>`

            results_table.appendChild(tr)
        }

        //console.table(summary_judgement)

        const anchor = foobar['summary']
        const anchor_table = document.querySelector('.anchor-body table tbody')
        anchor_table.innerHTML = ''

        for(const key of Object.keys(anchor))
        {
            const value = anchor[key]
            const [slno, type] = key.split(';')

            const tr = document.createElement('tr')
            tr.innerHTML = `<td>${slno}</td> <td>${type.split('.')[0]}</td> <td>${value}</td>`
            anchor_table.appendChild(tr)
        }
    })
})

function buttonClick(a) {
    switch(a.target.id) {
        case 'start-recording':
            buttons['stop-recording'].disabled=false;
            buttons['start-recording'].disabled=true;

            conn_status.classList.add('control-status-yup')
            conn_status.classList.remove('control-status-nope')
            conn_status.innerHTML = 'Recording'

            recorder.start();
            break;

        case 'stop-recording':
            buttons['stop-recording'].disabled=true;
            buttons['start-recording'].disabled=false;

            conn_status.classList.remove('control-status-yup')
            conn_status.classList.add('control-status-nope')
            conn_status.innerHTML = 'Not Recording'

            recorder.stop();
            break;
    }
}

function loadButtons() {
    const keys = Object.keys(buttons)
    for(const a of keys) {
        buttons[a] = document.getElementById(a)
        buttons[a].addEventListener('click', buttonClick)
    }
}

function main() {
    loadButtons()
}

main()
