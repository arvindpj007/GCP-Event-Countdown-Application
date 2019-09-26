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

async function deleteEvent(name,date) {
    console.log('delete:'+name+date);

    await reqJSON('POST','/delete', date+' '+name)
    .then(({status, data}) =>{
        if(data != null)
            alert('The event with name: ' + name + ' and date: ' + date + ' are deleted');
        else {
            alert('Session Expired');
            window.location='/loginPage';
        }
        reqJSON('GET','/');
        document.location.reload();
    });

}

async function logout(){
    await reqJSON('GET','/logoutUser');
    alert('User Logged Out');
    window.location='/loginPage';
}

async function get_events()
{
    return await reqJSON('GET', '/events');
}

async function delete_negative_timer(date,name)
{
    return await reqJSON('POST','/delete', date+' '+name);
}

document.addEventListener('DOMContentLoaded', () => {

  get_events()
  .then(({status, data}) => {

  setInterval(function () {

    let html = '<table id="table">' +
        '<tr>\n' +
        '    <th>Event Name</th>\n' +
        '    <th>Event Date (dd-mm-yyyy)</th> \n' +
        '    <th>Time Left (d:h:m:s)</th>\n' +
        '    <th>Click To Delete</th>\n' +
        '  </tr>';


    for (let event of data.events) {
        var datest = event.date.split('-');
        var target = new Date(+datest[2], datest[1]-1, +datest[0]);
        var time = Math.floor((+target - new Date()) / 1000);

        if(time<=0)
        {
           //console.log('negative countdown')
            delete_negative_timer(event.date.toString(),event.name.toString())
            .then(({status, data}) =>{
                alert('The event with name: ' + event.name.toString() + ' and date: ' + event.date.toString() + ' are deleted');
                document.location.reload();
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

            html += `<form onsubmit="false"><tr><td>${event.name} </td> <td> ${event.date} </td><td> ${day}:${hour}:${minute}:${second}</td><td><input type="button" name=${event.name}+'-'+${event.date} value="REMOVE" onclick="deleteEvent(\'${event.name}\',\'${event.date}\')"></td></tr></form>`;
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
      //alert('clicked');
    if( !document.getElementById('name').value || !document.getElementById('date').value)
        alert("either name or date is not entered ");
    else {

        var datest = document.getElementById('date').value.split('-');
        var target = new Date(+datest[0], datest[1]-1, +datest[2]);
        var time = Math.floor((+target - new Date()) / 1000);
        console.log(datest);
        console.log(time);
        if(time<=0)
        {
            alert('Event cannot be made, The date provided is already passed');
            reqJSON('GET','/');
        }
        else
        {
            var data = document.getElementById('name').value + ' ' + document.getElementById('date').value;
            reqJSON('POST','/event', data)
            .then(({status, data}) =>{
                if(data != null)
                    alert('event made successfully with id: '+ data);
                else
                {
                    alert('Session Expired');
                    window.location='/loginPage';
                }

            });
        }
    }
    document.location.reload();
  });
});


// $.ajax({
//     type: "POST",
//     url: "/event",
//     dataType: "json",
//     data: document.getElementById('name').value + ' ' + document.getElementById('date').value,
//     success: function (data) {
//         console.log('Success');
//         alert("Event created with id: "+data+" name: " + document.getElementById('name').value + " and date: " + document.getElementById('date').value);
//         document.location.reload();
//     },
//     error: function () {
//         console.log('Error');
//     }
// });

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
