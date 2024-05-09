let jobTypes = {};
let linkTypes = {};
let mimeTypes = {};
let currentSrcType;

function createJobBlock(jobType, jobName) {
    return `<div class="job-block">
                <p>${jobName}</p>
                <input name="job" type="hidden" value="${jobType}">
                <input type="button" class="default-btn default-btn--circle delete-btn">
            </div>`;
}

function createDateFieldMenu(params) {
    let firstFieldId = params[0];
    let listLi = []
    for (let i = 0; i < params.length; i++) {
        listLi.push(`<li id="${params[i]}">${params[i]}</li>`)
    }
    return `<div class="default-dropdown dropdown">
                <div class="select">
                    <span>${firstFieldId}</span>
                </div>
                <ul class="dropdown-menu">
                ${listLi.join('\n')}
                </ul>
                <input name="date_field" type="hidden" class="request" value="${firstFieldId}">
            </div>`
}

function createJobBlockWithParams(jobType, jobName, paramList) {
    return `<div class="job-block">
                <div class="job-input-block">
                    <p>${jobName}</p>
                    <input name="job" type="hidden" value="${jobType}">
                    ${paramList.join('\n')}
                </div>
                <input type="button" class="default-btn default-btn--circle delete-btn">
            </div>`;
}

function createParam(type, text) {
    return `<input name="param" type="hidden" value="${type}">
            <input name="param_value" type="text" class="form-input" placeholder="Вставьте ${text}" required>`;
}

function createJobLi(job, group, params_list) {
    return `<li onclick="addJob('blockId','${job.name}','${group.group_name}/${job.title}',[${params_list}])">${job.title}</li>`;
}

function createTitleLi(title) {
    return `<li class="title">${title}:</li>`;
}

function createFieldBlock(name, type, index) {
    return `<div id="${index}" class="field-block">
                <input name="field_name" type="hidden" value='${name}'>
                <input name="type" type="hidden" value="${type}">          
                <div class="title-block">
                    <p>${name}</p>
                    <input type="button" class="default-btn default-btn--circle delete-btn">
                </div>
                <div class="job-list">
                    <div class="job-block">
                        <p>Загрузить в конвейер</p>
                    </div>
                </div>
                <input type="button" class="default-btn default-btn--circle add-btn">
                <div class="job-dropdown dropdown">
                    <ul class="dropdown-menu">
                    ${jobTypes[type](index)}
                    </ul>
                </div>
            </div>`;
}

$('.exit-btn').on('click', function () {
   window.location.replace("/pipelines");
})

function isInt(n) {
   return n % 1 === 0;
}

function convertToBool(strBool) {
    return strBool === "" || strBool === "true";
}

function addJob(blockId, jobType, jobName, params) {
    let jobList = $(`#${blockId} .job-list`);
    let jobBlock;

    if (params.length > 0) {
        let paramList = [];
        params.forEach((x) => {
            let values = x.split(':');
            paramList.push(createParam(values[0], values[1]));
        });
        jobBlock = createJobBlockWithParams(jobType, jobName, paramList);
    }
    else jobBlock = createJobBlock(jobType, jobName);

    jobList.append(jobBlock);
    $(`#${blockId}`).find('.dropdown-menu').hide();
}

window.addEventListener("load", (event) => {
    $.get( "jobs", function( data ) {
        data.jobs.forEach((type) => {
            let liList = [];
            type.job_list.forEach((group) => {
                liList.push(createTitleLi(group.group_name));
                group.jobs.forEach((job) => {
                    if (job.params.length > 0) {
                        let params_list = [];
                        job.params.forEach((x) => params_list.push(`'${x.name}:${x.value}'`));
                        liList.push(createJobLi(job, group, params_list));
                        console.log(createJobLi(job, group, params_list))
                    }
                    else liList.push(createJobLi(job, group, []));
                })
            })
            let result = liList.join('\n');
            jobTypes[type.type] = id => result.replaceAll("blockId", id);
        });

        data.links.forEach((link) => {
            linkTypes[link.name] = [];
            link.value.regex.forEach((reg) => linkTypes[link.name].push(new RegExp(reg)));
        })

        data.files.forEach((file) => {
            mimeTypes[file.name] = file.value.extensions.join(',');
        })
    });
});

function raiseErrorMsg(errorId, message) {
    let error = $(errorId);
    error.text(message);
    error.slideDown('slow');
    setTimeout(function () { error.slideUp('slow'); }, 3000);
}

function changeNumInput(min, max, visibleId) {
    $('.time-input').attr({
       "max" : max,
       "min" : min
    });
    $('.time-input').val(min);
    switchVisible('.not-ok', '.ok');
    $(visibleId).fadeIn('slow');
}

$('body').on('change', '.time-input', (function () {
    let max = parseInt($(this).attr('max'));
    let min = parseInt($(this).attr('min'));
    let value = parseFloat($(this).val());
    let timeType = $(this).parents('.time-input-block').find('span').text();
    if (value > max)
    {
        let message = `Максимально допустимое значение единицы "${timeType}" - ${max}`;
        raiseErrorMsg('.time-error-msg', message);
        $(this).val(max);
    }
    else if (value < min)
    {
        let message = `Минимально допустимое значение единицы "${timeType}" - ${min}`;
        raiseErrorMsg('.time-error-msg', message);
        $(this).val(min);
    }
    else if (!isInt(value)) {
        let message = "Допустимы только целые числа";
        raiseErrorMsg('.time-error-msg', message);
        $(this).val(Math.round(value));
    }
}));

function switchToNextPage(sourceId, targetId){
    $(sourceId).animate({
        opacity: 'hide',
        marginLeft: '-50px'
    }, 'slow', 'linear', function() {
        $(this).css('margin',  'auto');
        $(this).hide();
    });
    setTimeout(() => {
        $(targetId).fadeIn('slow');
    }, 650);
}

function setHiddenValue(targetId, value){
    $(targetId).attr('value', value);
}

$('#file-type-pnl .default-btn--big').on('click', function() {
	$('.input-file input[type=file]').attr("accept", mimeTypes[$(this).val()]);
});

function setVisible(targetId){
    $(targetId).show();
}

function setInvisible(targetId){
    $(targetId).hide();
}

function switchVisible(hideId, showId) {
    $(hideId).hide();
    $(showId).show();
}

function hideAndClean(sourceId) {
    let childHide = document.querySelectorAll(`${sourceId} .hidden`);
    $.each(childHide, function() {
        $(this).hide();
    });

    let childClear = document.querySelectorAll(`${sourceId} input[type="text"],
                                                        ${sourceId} input[type="hidden"],
                                                        ${sourceId} input[type="file"],
                                                        ${sourceId} input[type="number"],
                                                        ${sourceId} input[type="password"]`);
    $.each(childClear, function() {
        $(this).val('');
    });

    let childDropdown = document.querySelectorAll(`${sourceId} .dropdown .select span`);
    $.each(childDropdown, function () {
        $(this).text("Выберите вариант");
    });
}

function clickToAdd(targetId, removeId){
    if (targetId.length > 0)
        $(targetId).show();
    if (removeId.length > 0)
        $(removeId).hide();
}

$('body').on('click', '.default-dropdown', (function () {
    $(this).toggleClass('active');

    if (document.getElementById('table-row')) {
        let inputs = [...document.getElementsByClassName('dropdown-types')];
        if (inputs.every(x => !x.classList.contains('active'))) {
            setTimeout(function() {
                $('#table-container').height(140);
            }, 300);
        }
        else {
            $('#table-container').height(290);
        }
    }

    $(this).find('.dropdown-menu').slideToggle(300);
}));

$('body').on('click', '.default-dropdown .dropdown-menu li',function () {
    $(this).parents('.default-dropdown').find('span').text($(this).text());
    $(this).parents('.default-dropdown').find('input').attr('value', $(this).attr('id'));
});

function checkRows() {
    let row = document.querySelectorAll(`#row-pnl .request`);
    let data = {};

    $.each(row, function (i, l) {
        if (l.name.includes('auto'))
            data[l.name] = convertToBool(l.value);
        else
            data[l.name] = l.value;
    });

    data["file_type"] = $('[name="file_type"]').val()

    jQuery.ajax({
        url: 'parse',
        type: 'POST',
        data:  JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success: function (result) {
            let table = $("#table-container");
            table.html(result.html);
            table.height(145);
            $('#save-table-block .default-btn--little').attr('onClick', "switchToNextPage('#table-pnl','#row-pnl')");
            switchToNextPage("#row-pnl", "#table-pnl");
        }
    }).fail(function (response) {
        let data = jQuery.parseJSON(response.responseText);
        let message = data.detail.msg;
        raiseErrorMsg('#validation-error-msg', message);
    });
}

function collectKeys() {
    let keys = $('[name="key"]');
    let result = [];

     $.each(keys, function (index, val) {
         result.push($(val).val());
    });

    return result;
}

$('.db-set .check-btn').on('click', function() {
    let connectId = $(this).parents('.db-set').attr('id');
    let errorMsgId = $(this).parents('.db-set').find('.error-msg').attr('id');
	let row = document.querySelectorAll(`#${connectId} .request`);
    let data = {};

    $.each(row, function (i, l) {
            data[l.name] = l.value;
    });

    data['db_type'] = $('[name="db_type"]').val();
    if (connectId === "mongo-set")
        data["key"] = collectKeys()

    console.log(data)
    jQuery.ajax({
        url: 'connect',
        type: 'POST',
        data:  JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success: function (result) {
            let table = $("#table-container");
            table.html(result.html);
            table.height(145);
            $('#save-table-block .default-btn--little').attr('onClick', `switchToNextPage('#table-pnl','#${connectId}')`);
            switchToNextPage(`#${connectId}`, "#table-pnl");
        }
    }).fail(function (response) {
        let data = jQuery.parseJSON(response.responseText);
        let message = data.detail.msg;
        raiseErrorMsg(`#${errorMsgId}`, message);
    });
});

$('#all').on('click', function () {
    $('.date-field-block').hide();
    $('#date_field').removeClass('selected');
    $(this).addClass('selected');
    $('[name="upload_schema"]').val($(this).attr('id'));
})

$('#file-type-pnl .default-btn--big').on('click', function () {
    $('[name="file_type"]').val($(this).val());
})

$('#date_field').on('click', function () {
    $('.date-field-block').show();
    $('#all').removeClass('selected');
    $(this).addClass('selected');
    $('[name="upload_schema"]').val($(this).attr('id'));
})

$('.add-key-btn').on('click', function() {
    let addKeyBlock = $('#add-key-block');
    addKeyBlock.append(`<div class="key-block">
                             <input name="key" type="text" class="form-input" placeholder="Введите имя ключа">
                             <input type="button" class="default-btn cancel-btn">
                         </div>`)
});

$('body').on('click', '.key-block .cancel-btn',function () {
    let keyBlock = $(this).parents('.key-block');
    keyBlock.remove();
});

function saveTable() {
    currentSrcType = `#src-${$('#src-type').val()}`;
    let tdType = document.querySelectorAll(`#table-container .type`);
    let tdTitle = document.querySelectorAll('#table-container th')
    let fieldMenu = $('.field-dropdown .dropdown-menu');
    let dateFields = []

    $.each(tdType, function(i, td) {
        let fieldName = $(tdTitle[i]).text();
        let fieldType = $(td).find('input[type="hidden"]').val();

        if (fieldType === "date" || fieldType === "datetime")
            dateFields.push(fieldName);

        $(td).html($(td).find('span').text());
        $(this).removeClass('type');
        fieldMenu.append(`<li class="${fieldType}">${fieldName}</li>`);
        $('#create-pipeline').append(`<input name="titles[]" type="hidden" value='${fieldName}'>`)
    });

    if (dateFields.length === 0)
        $('.date-field-block').append(`<div><p>Нет полей дата/время</p></div>`)
    else
        $('.date-field-block').append(createDateFieldMenu(dateFields))

    $('[name="field_count"]').val(tdTitle.length);
    $('#table-row').addClass('save');
    $('#table-container').height(140);
    $('#save-table-block').hide();
    $('#change-table-block').show();
    $('.set-job').fadeIn('slow');
}

function editSource() {
    hideAndClean('#file-type-pnl');
    hideAndClean('#db-type-pnl');
    hideAndClean('#postgres-set');
    hideAndClean('#mongo-set');
    hideAndClean('#row-pnl');
    $('[name="titles[]"]').remove();
    $(currentSrcType).fadeOut('slow');
    $('.set-job').fadeOut('slow');
    $('#change-table-block').fadeOut('slow');

    switchToNextPage('#table-pnl','#src-type-pnl');

    setTimeout(function() {
        $(`.job-group`).empty();
        $('.field-dropdown .dropdown-menu').empty();
        $('.date-field-block div').remove();
        switchVisible('#open-table-menu-block', '#table-menu-btn');
        setVisible('#save-table-block');
        hideAndClean('#add-file');
        hideAndClean('#link-pnl')
        setInvisible(`${currentSrcType} .submit-btn`);
    }, 650);
}

$('body').on('click', '.add-job-btn', (function () {
    $(`.add-job-btn`).hide();
    $(`.field-dropdown`).show();
}));

$('body').on('click', '.field-dropdown .dropdown-menu li', (function () {
    let index = $(this).index();
    let jobBlock = createFieldBlock($(this).text(), $(this).attr('class'), index);
    let jobGroup = $('.job-group');

    $(this).hide();
    jobGroup.append(jobBlock);
    switchVisible('.field-dropdown', '.add-job-btn');

    let jobCount = jobGroup.children('.field-block').length;
    if (jobCount === 1)
        $(currentSrcType).fadeIn('slow');
}));

$('.open-eye-btn').on('click', function () {
    $(this).toggleClass('close-eye-btn');
    let x = $('[name="password"]')
    if (x.attr('type') === "password") {
        x.attr('type', "text");
    } else {
        x.attr('type', "password");
    }
})

$('body').on('click', '.field-dropdown .cancel-btn', (function () {
    switchVisible('.field-dropdown', '.add-job-btn');
}));

$('body').on('click', '.field-block .title-block .delete-btn', (function () {
    let fieldBlock = $(this).parents('.field-block');
    let index = Number(fieldBlock.attr('id'));
    let jobCount = $('.job-group').children('.field-block').length;

    if (jobCount === 1)
        $(currentSrcType).fadeOut('slow');

    $('.field-dropdown .dropdown-menu li').eq(index).show();
    fieldBlock.remove();
}))

$('body').on('click', '.add-btn', (function () {
    $(this).parents('.field-block').find('.job-dropdown .dropdown-menu').show();
}))

$('body').on('click', '.job-block .delete-btn', (function () {
    $(this).parents('.job-block').remove();
}))

$('.input-file input[type=file]').on('change', function() {
	let file = this.files[0];
    let fileName = $(this).closest('.input-file').parents('.input-file-block').find('.file-name');
    fileName.find('p').text(file.name);
    fileName.show();
    $(`${currentSrcType} .submit-btn`).fadeIn('slow');
});

$('input[name="link"]').on('change', function() {
	let link = $(this).val();
    let type = $('#link-type').val();
    let flag = false;
    linkTypes[type].forEach((reg) => {
        if (reg.test(link)) {
            $(`${currentSrcType} .submit-btn`).fadeIn('slow');
            flag = true;
        }
    })
    if (!flag) {
        $(this).val('');
        $(`${currentSrcType} .submit-btn`).fadeOut('slow');
        raiseErrorMsg('#link-validation-error-msg', 'Неправильный формат ссылки');
    }
});

function getListOfInputValues(target) {
    let inputs = $(target);
    let result = [];

    $.each(inputs, function (i, l) {
        result.push(l.value)
    });

    return result;
}

function getAllJobs() {
    let fields = $('.job-group .field-block');
    let result = [];

     $.each(fields, function (fieldIndex, fieldValue) {
         let field = {
             "field_name": $(fieldValue).find('[name="field_name"]').val(),
             "type": $(fieldValue).find('[name="type"]').val(),
             "job_list": []
         };
         let jobs = $(fieldValue).find('.job-block');
         $.each(jobs, function (jobIndex, jobValue) {
             if (jobIndex > 0) {
                 let job = {
                     "name": $(jobValue).find('[name="job"]').val(),
                     "param": getListOfInputValues($(jobValue).find('[name="param"]')),
                     "param_value": getListOfInputValues($(jobValue).find('[name="param_value"]'))
                 };
                 field["job_list"].push(job);
             }
         });
         result.push(field);
    });
    return result;
}

function getFileFormData() {
    let formData = new FormData();
    let data = {
        "name": $('[name="name"]').val(),
        "auto_sep": convertToBool($('[name="auto_sep"]').val()),
        "sep": $('[name="sep"]').val(),
        "auto_title": convertToBool($('[name="auto_title"]').val()),
        "titles": getListOfInputValues('[name="titles[]"]'),
        "example": $('[name="example"]').val(),
        "field_job": getAllJobs()
    };
    formData.append("data", JSON.stringify(data));
    formData.append("file", $('[name="file"]')[0].files[0]);
    return formData;
}

function getLinkFormData() {
    let data = {
        "name": $('[name="name"]').val(),
        "auto_sep": convertToBool($('[name="auto_sep"]').val()),
        "sep": $('[name="sep"]').val(),
        "auto_title": convertToBool($('[name="auto_title"]').val()),
        "titles": getListOfInputValues('[name="titles[]"]'),
        "example": $('[name="example"]').val(),
        "field_job": getAllJobs(),
        "link_type": $('[name="link_type"]').val(),
        "link": $('[name="link"]').val(),
        "period": $(`${currentSrcType} input[name="period"]`).val(),
        "period_value": $(`${currentSrcType} input[name="period_value"]`).val()
    };
    return JSON.stringify(data);
}

function getDBFormData() {
    let dbType = $('[name="db_type"]').val();
    let dbId;
    if (dbType === "mongodb")
        dbId = "#mongo-set"
    else
        dbId = "#postgres-set"
    let data = {
        "name": $('[name="name"]').val(),
        "db_type": $('[name="db_type"]').val(),
        "db_name": $(`${dbId} [name="db_name"]`).val(),
        "db_auth": $('[name="db_auth"]').val(),
        "schema": $('[name="schema"]').val(),
        "date_field": $('[name="date_field"]').val(),
        "upload_schema": $('[name="upload_schema"]').val(),
        "host": $(`${dbId} [name="host"]`).val(),
        "port": $(`${dbId} [name="port"]`).val(),
        "table": $(`${dbId} [name="table"]`).val(),
        "username": $(`${dbId} [name="username"]`).val(),
        "password": $(`${dbId} [name="password"]`).val(),
        "field_job": getAllJobs(),
        "period": $(`${currentSrcType} input[name="period"]`).val(),
        "period_value": $(`${currentSrcType} input[name="period_value"]`).val()
    };
    return JSON.stringify(data);
}

let preparedFormData = {
    "file": getFileFormData,
    "link": getLinkFormData,
    "database": getDBFormData
}

function sendData() {
    let type = currentSrcType.replace('#src-', '');
    let data = preparedFormData[type]();

    if (type === 'file')
        sendMultipartData(type, data);
    else
        sendJsonData(type, data);
}

async function sendMultipartData(type, data) {
    try {
        const response = await fetch(`/pipelines/${type}`, {
            method: "POST",
            body: data
        });
        let responseData = await response.json();
        if (response.ok)
            window.location.replace("/pipelines");
        else {
            raiseErrorMsg(".create-error-msg", responseData.detail.msg)
        }
    } catch (e) {
         console.log(e)
    }

}

async function sendJsonData(type, data) {
    console.log(data)
    try {
        let response = await fetch(`/pipelines/${type}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: data,
        });
        let responseData = await response.json();
        if (response.ok)
            window.location.replace("/pipelines");
        else {
            raiseErrorMsg(".create-error-msg", responseData.detail.msg)
        }
    } catch (e) {
        console.error(e);
    }
}

document.querySelector("#create-pipeline").addEventListener("submit", (event) => {
    event.preventDefault();
    sendData();
});


