let chartType = {};
let menuChartX = [];
let menuChartY = {"num": [], "str": []};
let versions = [];
let fields = {};
let totalChartCount = 0;

$('.exit-btn').on('click', function () {
   window.location.replace("/pipelines");
})

function switchToNextPage(sourceId, targetId){
    $(sourceId).animate({
        opacity: 'hide'
    }, 'slow', 'linear', function() {
        $(this).hide();
    });
    setTimeout(() => {
        $(targetId).fadeIn('slow');
    }, 650);
}

function raiseErrorMsg(errorId, message) {
    let error = $(errorId);
    error.text(message);
    error.slideDown('slow');
    setTimeout(function () { error.slideUp('slow'); }, 3000);
}

function isInt(n) {
   return n % 1 === 0;
}

$('body').on('change', '[name="slice_start"], [name="slice_end"]', (function () {
    let chartId = $(this).parents('.chart-block').attr('id');
    let max = parseInt($(this).attr('max'));
    let min = parseInt($(this).attr('min'));
    let value = parseFloat($(this).val());
    if (value > max)
    {
        let message = `Максимально допустимое значение ${max}`;
        raiseErrorMsg(  `#${chartId} .slice-error-msg `, message);
        $(this).val(max);
    }
    else if (value < min)
    {
        let message = `Минимально допустимое значение ${min}`;
        raiseErrorMsg(  `#${chartId} .slice-error-msg `, message);
        $(this).val(min);
    }
    else if (!isInt(value)) {
        let message = "Допустимы только целые числа";
        raiseErrorMsg(  `#${chartId} .slice-error-msg `, message);
        $(this).val(Math.round(value));
    }
}));

function getData(id) {
    let curChartType = $(`#${id} [name="chart_type"]`).val();
    let data;
    if (chartType[curChartType]["type"] === "one") {
        data = {
            "chart_type": curChartType,
            "version": [$(`#${id} .single-chart-version-block [name="version"]`).val()],
            "x_direct": $(`#${id} .single-chart-direct-type-block [name="x_direct"]`).val(),
            "x_aggreg": $(`#${id} .single-chart-direct-type-block [name="x_aggreg"]`).val()
        }
    } else if (chartType[curChartType]["type"] === "mixed") {
         data = {
            "chart_type": curChartType,
            "version": [$(`#${id} .mixed-chart-version-block [name="version"]`).val()],
            "x_direct": $(`#${id} .mixed-chart-direct-type-block [name="x_direct"]`).val(),
            "y_direct": $(`#${id} .mixed-chart-direct-type-block [name="y_direct"]`).val()
        }
    } else {
         data = {
            "chart_type": curChartType,
            "version": getListVersion(id),
            "x_direct": $(`#${id} .multi-chart-direct-type-block [name="x_direct"]`).val(),
            "x_aggreg": $(`#${id} .multi-chart-direct-type-block [name="x_aggreg"]`).val(),
            "y_direct": $(`#${id} .multi-chart-direct-type-block [name="y_direct"]`).val(),
            "y_aggreg": $(`#${id} .multi-chart-direct-type-block [name="y_aggreg"]`).val(),
        }
    }
    jQuery.ajax({
        url: '/pipelines/chart',
        type: 'POST',
        data:  JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success: function (result) {
            if (!(chartType[curChartType]["type"] === 'mixed')) {
                let dataset = []
                for (let i = 0; i < result.versions.length; i++) {
                    dataset.push({
                        label: result.versions[i],
                        data: result.data[i],
                        borderWidth: 1
                    })
                }
                let ctx = document.getElementById(`chart-${id}`);
                new Chart(ctx, {
                    type: curChartType.replace('_chart', ''),
                    data: {
                        labels: result.labels,
                        datasets: dataset
                    },
                    options: {
                        plugins: {
                            legend: {
                                display: !(curChartType.replace('_chart', '') === 'pie'),
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                            x: {
                                display: false
                            }
                        }
                    }
                });
            } else {
                let ctx = document.getElementById(`chart-${id}`);
                new Chart(ctx, {
                    type: curChartType.replace('_chart', ''),
                    data: {
                        datasets:  [
                            {
                                label: `${result.min} < ${result.label} < ${result.max}`,
                                data: result.data
                                    .filter(row => result.min < row.y && row.y < result.max)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            },
                            {
                                label: `${result.label} >= ${result.max}`,
                                data: result.data
                                    .filter(row => row.y >= result.max)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            },
                            {
                                label: `${result.label} <= ${result.min}`,
                                data: result.data
                                    .filter(row => row.y <= result.min)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            }
                        ]
                    },
                    options: {
                        plugins: {
                            legend: {
                                display: !(curChartType.replace('_chart', '') === 'pie'),
                            }
                        }
                    }
                });
            }
            if (chartType[curChartType]["type"] === "one") {
                switchToNextPage(`#single-chart-direct-type-block-${id}`, `#done-chart-${id}`);
                $(`#${id} [name="slice_end"]`).val(result.data[0].length);
            } else if (chartType[curChartType]["type"] === "mixed") {
                switchToNextPage(`#mixed-chart-direct-type-block-${id}`, `#done-chart-${id}`);
                $(`#${id} [name="slice_end"]`).val(result.data.length);
            } else {
                switchToNextPage(`#chart-direct-type-block-${id}`, `#done-chart-${id}`);
                $(`#${id} [name="slice_end"]`).val(result.data[0].length);
            }
            $(`#${id} [name="slice_start"]`).attr('max', result.count);
            $(`#${id} [name="slice_end"]`).attr('max', result.count);
        }
    }).fail(function (response) {
        let data = jQuery.parseJSON(response.responseText);
        let message = data.detail.msg;
        console.log(message)
        raiseErrorMsg('#validation-error-msg', message);
    });
}

function getNewData(id) {
    let curChartType = $(`#${id} [name="chart_type"]`).val();
    let data;
   if (chartType[curChartType]["type"] === "one") {
        data = {
            "chart_type": curChartType,
            "version": [$(`#${id} .single-chart-version-block [name="version"]`).val()],
            "x_direct": $(`#${id} .single-chart-direct-type-block [name="x_direct"]`).val(),
            "x_aggreg": $(`#${id} .single-chart-direct-type-block [name="x_aggreg"]`).val()
        }
    } else if (chartType[curChartType]["type"] === "mixed") {
         data = {
            "chart_type": curChartType,
            "version": [$(`#${id} .mixed-chart-version-block [name="version"]`).val()],
            "x_direct": $(`#${id} .mixed-chart-direct-type-block [name="x_direct"]`).val(),
            "y_direct": $(`#${id} .mixed-chart-direct-type-block [name="y_direct"]`).val()
        }
    } else {
         data = {
            "chart_type": curChartType,
            "version": getListVersion(id),
            "x_direct": $(`#${id} .multi-chart-direct-type-block [name="x_direct"]`).val(),
            "x_aggreg": $(`#${id} .multi-chart-direct-type-block [name="x_aggreg"]`).val(),
            "y_direct": $(`#${id} .multi-chart-direct-type-block [name="y_direct"]`).val(),
            "y_aggreg": $(`#${id} .multi-chart-direct-type-block [name="y_aggreg"]`).val(),
        }
    }
    data["slice_start"] = $(`#${id} [name="slice_start"]`).val();
    data["slice_end"] = $(`#${id} [name="slice_end"]`).val();
    jQuery.ajax({
        url: '/pipelines/chart',
        type: 'POST',
        data:  JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success: function (result) {
            let ctx = document.getElementById(`chart-${id}`);
            let chartStatus = Chart.getChart(`chart-${id}`);
            if (chartStatus) {
                chartStatus.destroy();
            }
            if (!(chartType[curChartType]["type"] === 'mixed')) {
                let dataset = []
                for (let i = 0; i < result.versions.length; i++) {
                    dataset.push({
                        label: result.versions[i],
                        data: result.data[i],
                        borderWidth: 1
                    })
                }
                let ctx = document.getElementById(`chart-${id}`);
                new Chart(ctx, {
                    type: curChartType.replace('_chart', ''),
                    data: {
                        labels: result.labels,
                        datasets: dataset
                    },
                    options: {
                        plugins: {
                            legend: {
                                display: !(curChartType.replace('_chart', '') === 'pie'),
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                            x: {
                                display: false
                            }
                        }
                    }
                });
            } else {
                let ctx = document.getElementById(`chart-${id}`);
                new Chart(ctx, {
                    type: curChartType.replace('_chart', ''),
                    data: {
                        datasets:  [
                            {
                                label: `${result.min} < ${result.label} < ${result.max}`,
                                data: result.data
                                    .filter(row => result.min < row.y && row.y < result.max)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            },
                            {
                                label: `${result.label} >= ${result.max}`,
                                data: result.data
                                    .filter(row => row.y >= result.max)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            },
                            {
                                label: `${result.label} <= ${result.min}`,
                                data: result.data
                                    .filter(row => row.y <= result.min)
                                    .map(row => ({
                                        x: row.x,
                                        y: row.y,
                                        r: row.count
                                    }))
                            }
                        ]
                    },
                    options: {
                        plugins: {
                            legend: {
                                display: !(curChartType.replace('_chart', '') === 'pie'),
                            }
                        }
                    }
                });
            }
        }
    }).fail(function (response) {
        let data = jQuery.parseJSON(response.responseText);
        let message = data.detail.msg;
        raiseErrorMsg('#validation-error-msg', message);
    });
}

function getListVersion(id) {
    let versions = $(`#${id}`).find('.multi-chart-version-block [name="version"]');
    let data = [];

    $.each(versions, function (i, l) {
        data.push(l.value);
    });

    return data;
}

function getListVersionForDownload() {
    let versions = $('.version-block-list [name="version"]');
    let data = [];

    $.each(versions, function (i, l) {
        data.push(l.value);
    });

    return data;
}

function createChartBlock(id) {
    return `<div class="chart-block" id="${id}">
                ${createChartTypeBlock(id)}
                ${createMultiVersionBlock(id)}
                ${createSingleVersionBlock(id)}
                ${createMixedVersionBlock(id)}
                ${createChartSetBlock(id)}
                ${createSingleChartSetBlock(id)}
                ${createMixedChartSetBlock(id)}
                ${createChart(id)}
            </div>`;
}

function createChartTypeBlock(id) {
    let buttonList = [];
    for (const [key, value] of Object.entries(chartType)) {
        if (value["type"] === "one") {
            buttonList.push(`<div class="chart-btn-type-block">
                                 <div class="chart-icon ${key}"></div>
                                 <input type="button" id="${key}" class="default-btn default-btn--big default-btn--violet" 
                                     value="${value['title']}" onclick="switchToNextPage('#chart-type-block-${id}', 
                                     '#single-chart-version-block-${id}')">
                             </div>`)
        } else if (value["type"] === "mixed") {
            buttonList.push(`<div class="chart-btn-type-block">
                                 <div class="chart-icon ${key}"></div>
                                 <input type="button" id="${key}" class="default-btn default-btn--big default-btn--violet" 
                                     value="${value['title']}" onclick="switchToNextPage('#chart-type-block-${id}', 
                                     '#mixed-chart-version-block-${id}')">
                             </div>`)
        } else {
            buttonList.push(`<div class="chart-btn-type-block">
                                 <div class="chart-icon ${key}"></div>
                                 <input type="button" id="${key}" class="default-btn default-btn--big default-btn--violet" 
                                     value="${value['title']}" onclick="switchToNextPage('#chart-type-block-${id}', 
                                     '#multi-chart-version-block-${id}')">
                              </div>`)
        }
    }
    return `<div id="chart-type-block-${id}" class="chart-type-block">
                ${buttonList.join('\n')}
                <input type="hidden" name="chart_type" value="">
            </div>`;
}

function createChart(id) {
    return `<div id="done-chart-${id}" class="chart-frame" style="display: none">
                <div class="chart-container">
                    <canvas id="chart-${id}"></canvas>
                </div>
                <div class="chart-settings">
                    <div class="amount-block">
                        <p>Установите промежуток, по которому будет отрисован график:</p>
                        <div class="amount-input-block">
                            <input name="slice_start" type="number" placeholder="Начало" value="0" min="0" max="">
                            —
                            <input name="slice_end" type="number" placeholder="Конец" value="" min="0" max="">
                        </div>
                        <div class="slice-error-msg error-msg" hidden="true">
                            <p></p>
                        </div>
                    </div>
                    <input type="button" class="default-btn default-btn--big default-btn--blue" onclick="getNewData(${id})" value="Перерисовать график">
                    <div class="create-delete-block">
                        <input type="button" class="delete-chart-btn">
                        <input type="button" class="add-chart-btn">
                    </div>
                </div>
            </div>`;
}

function createMultiVersionBlock(id) {
    return `<div class="multi-chart-version-block chart-version-block" id="multi-chart-version-block-${id}" style="display: none">
                <h2>Выберите версии данных, по которым будет строиться график</h2>
                ${versions.join('\n')}
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Далее" 
                    onclick="switchToNextPage('#multi-chart-version-block-${id}', '#chart-direct-type-block-${id}')">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#multi-chart-version-block-${id}','#chart-type-block-${id}')">
                </div>
            </div>`;
}

function createSingleVersionBlock(id) {
    return `<div class="single-chart-version-block chart-version-block" id="single-chart-version-block-${id}" style="display: none">
                <h2>Выберите версию данных, по которой будет строиться график</h2>
                ${versions.join('\n')}
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Далее" 
                    onclick="switchToNextPage('#single-chart-version-block-${id}', '#single-chart-direct-type-block-${id}')">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#single-chart-version-block-${id}','#chart-type-block-${id}')">
                </div>
            </div>`;
}

function createMixedVersionBlock(id) {
    return `<div class="mixed-chart-version-block chart-version-block" id="mixed-chart-version-block-${id}" style="display: none">
                <h2>Выберите версию данных, по которой будет строиться график</h2>
                ${versions.join('\n')}
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Далее" 
                    onclick="switchToNextPage('#mixed-chart-version-block-${id}', '#mixed-chart-direct-type-block-${id}')">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#mixed-chart-version-block-${id}','#chart-type-block-${id}')">
                </div>
            </div>`;
}

function createSingleChartSetBlock(id) {
    let menuFieldX = [];
    let table = [];
    table.push(`<table class=""><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<th>${value["name"]}</th>`);
        menuFieldX.push(`<li id="${key}">${value["name"]}</li>`);
    }
    table.push(`</tr><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<td>${value["type_name"]}</td>`);
    }
    table.push(`</tr></table>`)
    return `<div class="chart-direct-type-block single-chart-direct-type-block" id="single-chart-direct-type-block-${id}" style="display: none">
                <div class="table-block">${table.join('\n')}</div>
                <div class="direction-block-list">
                    <div class="x-block direction-block">
                        <div class="line-block">
                            <h2>Выберите поле, по которому будет отрисован график</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuFieldX.join('\n')}
                                </ul>
                                <input name="x_direct" type="hidden" value="">
                            </div>
                        </div>
                        <div class="line-block">
                            <h2>Выберите способ агрегации</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuChartX.join('\n')}
                                </ul>
                                <input name="x_aggreg" type="hidden" value="">
                            </div>
                        </div>
                    </div>
                </div>
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Создать график" 
                    onclick="getData(${id})">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#single-chart-direct-type-block-${id}', '#single-chart-version-block-${id}')">
                </div>
            </div>`;
}

function createChartSetBlock(id) {
    let table = [];
    let menuFieldX = [];
    let menuFieldY = [];
    table.push(`<table class=""><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<th>${value["name"]}</th>`);
        menuFieldX.push(`<li id="${key}">${value["name"]}</li>`);
        menuFieldY.push(`<li id="${key}" class="${value["type"]}">${value["name"]}</li>`);
    }
    table.push(`</tr><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<td>${value["type_name"]}</td>`);
    }
    table.push(`</tr></table>`)
    return `<div class="chart-direct-type-block multi-chart-direct-type-block" id="chart-direct-type-block-${id}" style="display: none">
                <div class="table-block">${table.join('\n')}</div>
                <div class="direction-block-list">
                    <div class="x-block direction-block">
                        <div class="title-block">
                            <div class="x-icon"></div>
                            <h2>X</h2>
                        </div>
                        <div class="line-block">
                            <h2>Выберите поле для направляющей X</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuFieldX.join('\n')}
                                </ul>
                                <input name="x_direct" type="hidden" value="">
                            </div>
                        </div>
                        <div class="line-block">
                            <h2>Выберите способ агрегации</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuChartX.join('\n')}
                                </ul>
                                <input name="x_aggreg" type="hidden" value="">
                            </div>
                        </div>
                    </div>
                    <div class="y-block direction-block">
                        <div class="title-block">
                            <div class="y-icon"></div>
                            <h2>Y</h2>
                        </div>
                        <div class="line-block">
                            <h2>Выберите поле для направляющей Y</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu y-field-dropdown">
                                    ${menuFieldY.join('\n')}
                                </ul>
                                <input name="y_direct" type="hidden" value="">
                            </div>
                        </div>
                        <div class="line-block">
                            <h2>Выберите способ агрегации</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu y-aggreg-dropdown">
                                </ul>
                                <input name="y_aggreg" type="hidden" value="">
                            </div>
                        </div>
                    </div>
                </div>
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Создать график" 
                    onclick="getData(${id})">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#chart-direct-type-block-${id}', '#multi-chart-version-block-${id}')">
                </div>
            </div>`;
}

function createMixedChartSetBlock(id) {
    let table = [];
    let menuField = [];
    table.push(`<table class=""><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<th>${value["name"]}</th>`);
        if (value["type"] === "num")
            menuField.push(`<li id="${key}">${value["name"]}</li>`);
    }
    table.push(`</tr><tr>`)
    for (const [key, value] of Object.entries(fields)) {
        table.push(`<td>${value["type_name"]}</td>`);
    }
    table.push(`</tr></table>`)
    return `<div class="chart-direct-type-block mixed-chart-direct-type-block" id="mixed-chart-direct-type-block-${id}" style="display: none">
                <div class="table-block">${table.join('\n')}</div>
                <div class="direction-block-list">
                    <div class="x-block direction-block">
                        <div class="title-block">
                            <div class="x-icon"></div>
                            <h2>X</h2>
                        </div>
                        <div class="line-block">
                            <h2>Выберите поле для направляющей X</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuField.join('\n')}
                                </ul>
                                <input name="x_direct" type="hidden" value="">
                            </div>
                        </div>
                    </div>
                    <div class="y-block direction-block">
                        <div class="title-block">
                            <div class="y-icon"></div>
                            <h2>Y</h2>
                        </div>
                        <div class="line-block">
                            <h2>Выберите поле для направляющей Y</h2>
                            <div class="default-dropdown dropdown">
                                <div class="select">
                                    <span>Выберите поле</span>
                                </div>
                                <ul class="dropdown-menu">
                                    ${menuField.join('\n')}
                                </ul>
                                <input name="y_direct" type="hidden" value="">
                            </div>
                        </div>
                    </div>
                </div>
                <input type="button" class="default-btn default-btn--big default-btn--aqua" value="Создать график" 
                    onclick="getData(${id})">
                <div class="back-block">
                    <input type="button" class="default-btn default-btn--little default-btn--grey" value="Назад"
                        onclick="switchToNextPage('#mixed-chart-direct-type-block-${id}', '#mixed-chart-version-block-${id}')">
                </div>
            </div>`;
}

window.addEventListener("load", (event) => {
    let parsedUrl = window.location.href.split('/');
    let pipelineId = parsedUrl.slice(-1);
    $.get( `/pipelines/info/${pipelineId}`, function( data ) {
        data.charts.forEach((chart) => {
            chartType[chart.name] = {"title": chart.value.title, "type": chart.value.type};
        });
        data.fields.forEach((field) => {
            fields[field.id] = {"name": field.name, "type": field.type, "type_name": field.type_name};
        });
        data.chartX.forEach((info) => {
            menuChartX.push(`<li id="${info.name}">${info.value}</li>`);
        });
        data.chartY.forEach((info) => {
            if (info.value.type.includes("num"))
                menuChartY["num"].push(`<li id="${info.name}">${info.value.title}</li>`)
            if (info.value.type.includes("str"))
                menuChartY["str"].push(`<li id="${info.name}">${info.value.title}</li>`)
        });
        data.versions.forEach((v) => {
            versions.push(`<div id="${v.id}" class="version-block">
                               <div class="radio-btn"></div>
                               <p>${v.name}</p>
                           </div>`);
        });
        $('#chart-list').append(createChartBlock(totalChartCount));
        totalChartCount = totalChartCount + 1;
    });
});

$('body').on('click', '.download-btn', function () {
    let data = {}
    let parsedUrl = window.location.href.split('/');
    let pipelineId = parsedUrl.slice(-1);
    data["pipeline_id"] = pipelineId[0];
    data["version"] = getListVersionForDownload();
    data["file_type"] = $('[name="file_type"]').val();
    let ajaxRequest = $.ajax({
        url: '/pipelines/download',
        type: 'POST',
        data:  JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
       success: function (result) {
            let link=document.createElement('a');
            link.href=`/pipelines/download/${result.file}`;
            link.download=result.file;
            link.click();
        }
    }).fail(function (response) {
        let data = jQuery.parseJSON(response.responseText);
        let message = data.detail.msg;
        raiseErrorMsg('#validation-error-msg', message);
    });
})

$('body').on('click', '.add-chart-btn', function () {
    $('#chart-list').append(createChartBlock(totalChartCount));
    totalChartCount = totalChartCount + 1;
})

$('body').on('click', '.delete-chart-btn', function () {
    $(this).parents('.chart-block').remove();
    totalChartCount = totalChartCount - 1;
})

$('body').on('click', '.default-dropdown', (function () {
    $(this).toggleClass('active');
    $(this).find('.dropdown-menu').slideToggle(300);
}));

$('body').on('click', '.chart-btn-type-block .default-btn', (function () {
    $(this).parents('.chart-type-block').find('[name="chart_type"]').attr('value', $(this).attr('id'));
}));

$('body').on('click', '.y-field-dropdown li',function () {
    let menu = $(this).parents('.y-block').find('.y-aggreg-dropdown');
    menu.empty();
    menu.append(menuChartY[$(this).attr('class')].join('\n'));
});

$('body').on('click', '.default-dropdown .dropdown-menu li',function () {
    $(this).parents('.default-dropdown').find('span').text($(this).text());
    $(this).parents('.default-dropdown').find('input').attr('value', $(this).attr('id'));
});

$('body').on('click', '.multi-chart-version-block .version-block', function () {
    if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
        $(this).parents('.multi-chart-version-block').find(`[value="${$(this).attr('id')}"]`).remove();
    } else {
        $(this).addClass('selected');
        $(this).parents('.multi-chart-version-block').append(`<input type="hidden" name="version" value="${$(this).attr('id')}">`);
    }
})

$('body').on('click', '.version-block-list .version-block', function () {
    if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
        $(this).parents('.version-block-list').find(`[value="${$(this).attr('id')}"]`).remove();
    } else {
        $(this).addClass('selected');
        $(this).parents('.version-block-list').append(`<input type="hidden" name="version" value="${$(this).attr('id')}">`);
    }
})

$('body').on('click', '.single-chart-version-block .version-block, .mixed-chart-version-block .version-block', function () {
    if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
        $(this).parents('.chart-version-block').find('[name="version"]').remove();
    } else {
        $(this).parents('.chart-version-block').find('.selected').removeClass('selected');
        $(this).parents('.chart-version-block').find('[name="version"]').remove();
        $(this).addClass('selected');
        $(this).parents('.chart-version-block').append(`<input type="hidden" name="version" value="${$(this).attr('id')}">`);
    }
})