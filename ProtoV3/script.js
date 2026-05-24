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

function construct_table(value) {
    const other_table = document.querySelector('.audio-prediction-spec table')

    const body = other_table.querySelector('tbody')
    body.innerHTML = ''

    for(let i = 0; i < value.timestamps.data.length; i++)
    {
        const at = value.timestamps.data[i];

        const scores = []
        const labels = []

        for(let j = 0; j < value.scores.data[i].length; j++)
        {
            labels.push(value.labels.data[i][j])
            scores.push(value.scores.data[i][j])
        }


        const tocompare = labels.join('');

        let predicted = (tocompare.match(/Horn|Honk/gi) || []).length
        predicted += (tocompare.match(/Car|Truck|Train|Bicycle/gi) || []).length / 2
        predicted += (tocompare.match(/Alarm|Buzzer|Bell/gi) || []).length / 4
        predicted += (tocompare.match(/Vehicle|Motor/gi) || []).length / 8
        predicted += (tocompare.match(/Music/gi) || []).length / 16
        predicted += (tocompare.match(/Whine|Screech|Brakes/gi) || []).length / 16

        const possible_total = 1 + 1/2 + 1/4 + 1/8 + 1/16 + 1/16;

        predicted = predicted / possible_total

        //const predicted = ((labels.join('').match(/Horn|Honk|Alarm|Buzzer|Bell/g) || []).length) / 5;

        //const predicted = value.predicted_horns.data[i][0]

        const val = `<tr>
            <td>${at}</td>

            <td style="background: hsl(${scores[0]}turn 60% 70%)">${labels[0]}</td>
            <td style="background: hsl(${scores[1]}turn 60% 70%)">${labels[1]}</td>
            <td style="background: hsl(${scores[2]}turn 60% 70%)">${labels[2]}</td>
            <td style="background: hsl(${scores[3]}turn 60% 70%)">${labels[3]}</td>
            <td style="background: hsl(${scores[4]}turn 60% 70%)">${labels[4]}</td>

            <td style="background: ${predicted > 0.5 ? "green" : "white"}">${predicted}</td>
        </tr>\n`

        body.innerHTML += val
    }
}


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

        if(recorded_audios[time]['stats'])
        {
            /*
            Plotly.newPlot('MFCCPlot', [
                {
                    z: recorded_audios[time]['melfrequencies'],
                    type: 'heatmap'
                }
            ])
            return;
            */

            return;
        }

        console.log(audio.srcObject)

        const data = new FormData()
        data.append('file', blb, "rotund.mp3")

        document.querySelector('#WooW').innerHTML = '<span style="font-size:2em;">LOADING...</span>'

        const value = await fetch('http://localhost:8080/recognize', {
            method: 'POST',
            body: data,
            mode: 'cors'
        })

        const values = await value.json()
        console.log(values)

        recorded_audios[time]['stats'] = values
        construct_table(values);

        /*
        Plotly.newPlot('MFCCPlot', [
            {
                z: melfrequencies,
                type: 'heatmap'
            }
        ], {
            xaxis: { title: {text: 'Time'} },
            yaxis: { title: {text: 'MFCC'} },
            title: { text: 'Mel-Frequency Cepstal Coffecients' },
        })

        document.querySelector('#WooW').innerHTML = ''
        */
    })

    //console.log(recorded_audios)
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
