$('.add-btn').on('click', function () {
    window.location.replace("/pipelines/add");
})

$('.stat-btn').on('click', function () {
    let pipelineId = $(this).parents('.btn-block').attr('id');
    window.location.replace(`/pipelines/stat/${pipelineId}`);
})

$('.exit').on('click', async function () {
    try {
        const response = await fetch(`/auth/logout`, {
            method: "POST"
        });
        if (response.ok)
            window.location.replace("/pipelines");
    } catch (e) {
    }
})
