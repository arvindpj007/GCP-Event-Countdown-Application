
function reqJSON(method, url, data) {
  return new Promise((resolve, reject) => {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.responseType = 'json';
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve({status: xhr.status, data: xhr.response});
      } else {
        reject({status: xhr.status, data: xhr.response});
      }
    };
    xhr.onerror = () => {
      reject({status: xhr.status, data: xhr.response});
    };
    xhr.send(data);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  reqJSON('GET', '/events')
  .then(({status, data}) => {
    // Use the *data* argument to change what we see on the page.
    // It will look something like this:
    // {
    //   "events": [
    //     {"name": "Grandma's Birthday", "date": "08-05"},
    //     {"name": "Independence Day", "date": "07-04"}
    //   ]
    // }

    // There are better ways, but this is illustrative of the concept:
    setInterval(function () {
        let html = '<table>' +
            '<tr>\n' +
            '    <th>Event Name</th>\n' +
            '    <th>Event Date (dd-mm-yyyy)</th> \n' +
            '    <th>Time Left (d:h:m:s)</th>\n' +
            '  </tr>';
    for (let event of data.events) {
        var datest = event.date.split('-');
        var target = new Date(+datest[2], datest[1]-1, +datest[0]);
        var time = Math.floor((+target - new Date()) / 1000);

        if(time<=0)
        {
           //console.log('negative countdown')
            $.ajax({
            type: "POST",
            url: "/delete",
            dataType: "json",
            data: event.date.toString()+' '+event.name.toString(),
            success: function (data) {
                console.log('Success');
                alert('The date you have entered is passed, hence it was automatically deleted')
                document.location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
        }
        else
        {
            var day = Math.floor(time / (24 * 3600));
            time = time % (24 * 3600);
            var hour = Math.floor(time / 3600);
            time %= 3600;
            var minute = Math.floor(time / 60);
            time %= 60;
            var second = Math.floor(time);

            html += `<tr><td>${event.name} </td> <td> ${event.date} </td><td> ${day}:${hour}:${minute}:${second}</td> </tr>`;
        }
    }
    document.getElementById('events').innerHTML = html;

    }, 1000);


  })
  .catch(({status, data}) => {
    // Display an error.
    document.getElementById('events').innerHTML = 'ERROR: ' +
      JSON.stringify(data);
  });
});


document.addEventListener('DOMContentLoaded',() =>{

  document.getElementById('create').addEventListener("click",()=> {
    if( !document.getElementById('name').value || !document.getElementById('date').value)
        alert("either name or date is not entered ");
    else {
        $.ajax({
            type: "POST",
            url: "/event",
            dataType: "json",
            data: document.getElementById('name').value + ' ' + document.getElementById('date').value,
            success: function (data) {
                console.log('Success');
                alert("Event created with id: "+data+" name: " + document.getElementById('name').value + " and date: " + document.getElementById('date').value);
                document.location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    }
  });
});

// function listner()
// {
//   const create_button = document.getElementById('create');
//   if(create_button)
//   {
//     var name= document.getElementById('name');
//     var date= document.getElementById('date');
//     create_button.addEventListener("click",function(){alert(name.value+date.value);});
//   }
//   else
//   {
//     alert('error');
//   }
// }
