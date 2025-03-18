class AsyncOptionsHandler {
    constructor(config) {
        this.config = {
            fetchUrl: config.fetchUrl,
            submitUrl: config.submitUrl,
            selectElementId: config.selectElementId,
            submitButtonId: config.submitButtonId,
            onFetch: config.onFetch || this.defaultOnFetch,
            onSubmit: config.onSubmit || this.defaultOnSubmit,
            errorHandler: config.errorHandler || this.defaultErrorHandler
        };
    }

    async fetchOptions() {
        try {
            const response = await fetch(this.config.fetchUrl);
            const options = await response.json();
            this.populateSelect(options);
            return options;
        } catch (error) {
            this.config.errorHandler(error, 'fetch');
        }
    }

    populateSelect(options) {
        const select = document.getElementById(this.config.selectElementId);
        select.innerHTML = ''; 
        options.forEach(option => {
            const optionElement = new Option(
                this.config.onFetch(option), 
                option
            );
            select.add(optionElement);
        });
    }

    async submitSelection() {
        const select = document.getElementById(this.config.selectElementId);
        const selectedOption = select.value;
        
        try {
            const response = await fetch(this.config.submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: `selected_option=${encodeURIComponent(selectedOption)}`
            });

            const result = await response.json();
            this.config.onSubmit(result, selectedOption);
            return result;
        } catch (error) {
            this.config.errorHandler(error, 'submit');
        }
    }

    // CSRF Token retrieval for Django
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    init() {
        this.fetchOptions();
        document.getElementById(this.config.submitButtonId)
            .addEventListener('click', () => this.submitSelection());
    }

    defaultOnFetch(option) {
        return option;
    }

    defaultOnSubmit(result, selectedOption) {
        console.log('Submitted:', result);
    }

    defaultErrorHandler(error, type) {
        console.error(`Error during ${type}:`, error);
    }
}