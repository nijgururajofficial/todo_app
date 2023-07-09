document.addEventListener('DOMContentLoaded', function() {
    const taskForm = document.querySelector('#taskForm');
    const taskTitleInput = document.querySelector('#taskTitleInput');
    const taskDescriptionInput = document.querySelector('#taskDescriptionInput');
    const taskList = document.querySelector('#taskList');

    // Add task
    taskForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const taskTitle = taskTitleInput.value.trim();
        const taskDescription = taskDescriptionInput.value.trim();
        if (taskTitle !== '') {
            addTask(taskTitle, taskDescription);
            taskTitleInput.value = '';
            taskDescriptionInput.value = '';
        }
    });

    // Complete task
    taskList.addEventListener('click', function(e) {
        if (e.target.classList.contains('completeCheckbox')) {
            const li = e.target.parentNode.parentNode;
            const number = li.getAttribute('data-number');
            completeTask(number);
            li.classList.toggle('completed');
        }
    });

    // Delete task
    taskList.addEventListener('click', function(e) {
        if (e.target.classList.contains('deleteBtn')) {
            const li = e.target.parentNode.parentNode;
            const number = li.getAttribute('data-number');
            deleteTask(number);
            li.remove();
        }
    });

    function addTask(title, description) {
        fetch('/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `task_title=${encodeURIComponent(title)}&task_description=${encodeURIComponent(description)}`
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }

    function completeTask(number) {
        fetch('/complete```', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `number=${encodeURIComponent(number)}`
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }

    function deleteTask(number) {
        fetch('/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `number=${encodeURIComponent(number)}`
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }
});
