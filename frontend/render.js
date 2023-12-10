document.getElementById('displaytext').style.display = 'none';

function searchPhoto() {
    var apigClient = apigClientFactory.newClient();

    var user_message = document.getElementById('note-textarea').value;

    var body = {};
    var params = {q: user_message};
    var additionalParams = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    apigClient
        .searchGet(params, body, additionalParams)
        .then(function (res) {
            var resp_data = res.data;
            console.log(resp_data)
            if (resp_data.imagePaths == "No Results found") {
                document.getElementById('displaytext').innerHTML =
                    'Sorry could not find the image. Try another search words!';
                document.getElementById('displaytext').style.display = 'block';
            }


            resp_data.imagePaths.forEach(function (obj) {
                var img = new Image();
                console.log(obj);
                img.src = obj;
                img.setAttribute('class', 'banner-img');
                img.setAttribute('alt', 'effy');
                document.getElementById('displaytext').innerHTML =
                    'Images returned are : ';
                document.getElementById('img-container').appendChild(img);
                document.getElementById('displaytext').style.display = 'block';
            });
        })
        .catch(function (result) {
        });
}

function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        // reader.onload = () => resolve(reader.result)
        reader.onload = () => {
            let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
            if (encoded.length % 4 > 0) {
                encoded += '='.repeat(4 - (encoded.length % 4));
            }
            resolve(encoded);
        };
        reader.onerror = (error) => reject(error);
    });
}

function uploadPhoto() {
    // var file = document.getElementById('file_path').files[0];
    console.log(file)
    const reader = new FileReader();
    document.getElementById('upload_button').innerHTML = 'Uploading...';
    document.getElementById('upload_button').style.backgroundColor = '#005af0';
    var file_data;
    var encoded_image = getBase64(file).then((data) => {
        console.log(data);
        var apigClient = apigClientFactory.newClient();

        var file_type = file.type + ';base64';
        console.log(file_type)
        var body = data;
        var params = {
            "object": file.name,
            'x-amz-meta-customLabels': note_customtag.value,
        };
        console.log(note_customtag.value)
        var additionalParams = {};
        apigClient
            .uploadObjectPut(params, body, additionalParams)
            .then(function (res) {
                if (res.status == 200) {
                    document.getElementById('upload_button').innerHTML = 'Upload succeeded';
                    document.getElementById('upload_button').style.backgroundColor = '#499C55';

                }
            }).catch(() => {
                document.getElementById('upload_button').innerHTML = 'Upload failed';
                document.getElementById('upload_button').style.backgroundColor = '#F54234';
            }
        );
    });
}


const dropArea = document.querySelector(".drop_box"),
    button = dropArea.querySelector("button"),
    dragText = dropArea.querySelector("header"),
    input = dropArea.querySelector("input");
let file;
var filename;

button.onclick = () => {
    input.click();
};

input.addEventListener("change", function (e) {
    var fileName = e.target.files[0].name;
    let filedata = `
    <h4>${fileName}</h4>
    <input placeholder="Input Custom tag!" type="text" class="form-control" id="note_customtag">
    <button class="btn" id="upload_button" type="submit" onclick="uploadPhoto()">Upload</button>
    `;
    file = document.getElementById('file_path').files[0];
    console.log(file)
    dropArea.innerHTML = filedata;
});

