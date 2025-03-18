function sendURL() {
    const urlInput = document.getElementById('floatingInput').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/process-url/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ url: urlInput }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseMessage').innerText = data.message;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
document.addEventListener('DOMContentLoaded', () => {
const optionsHandler = new AsyncOptionsHandler({
    fetchUrl: '{% url "get_database" %}',
    submitUrl: '{% url "process_selection" %}',
    selectElementId: 'floatingSelect',
    submitButtonId: 'dbSubmit',
    
    // Optional custom handlers
    onFetch: (option) => option.toUpperCase(),
    onSubmit: (result, selectedOption) => {
        document.getElementById('result').textContent = 
            `Selected: ${selectedOption}`;
    }
});

optionsHandler.init();
});
document.addEventListener('DOMContentLoaded', () => {
const optionsHandler = new AsyncOptionsHandler({
    fetchUrl: '{% url "get_tabel" %}',
    submitUrl: '{% url "tb_selection" %}',
    selectElementId: 'floatingSelect_1',
    submitButtonId: 'tbSubmit',
    
    // Optional custom handlers
    onFetch: (option) => option.toUpperCase(),
    onSubmit: (result, selectedOption) => {
        document.getElementById('result1').textContent = 
            `Selected: ${selectedOption}`;
    }
});

optionsHandler.init();
});
