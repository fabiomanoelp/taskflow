const taskForm = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const emptyState = document.querySelector("#empty-state");
const errorMessage = document.querySelector("#error-message");

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

async function request(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Não foi possível conectar à aplicação. Confira se o servidor está rodando e tente novamente.");
  }

  if (!response.ok) {
    let message = `A solicitação falhou (erro ${response.status}).`;
    try {
      const details = await response.json();
      if (details.detail) {
        message = Array.isArray(details.detail)
          ? "Confira os dados enviados e tente novamente."
          : details.detail;
      }
    } catch {
      // Algumas respostas de erro podem não conter JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

function formatDate(value) {
  const date = new Date(`${value.replace(" ", "T")}Z`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(date);
}

function makeTaskElement(task) {
  const item = document.createElement("li");
  item.className = `task-item${task.completed ? " is-completed" : ""}`;

  const checkbox = document.createElement("input");
  checkbox.className = "task-checkbox";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute("aria-label", `Marcar ${task.title} como concluída`);
  checkbox.addEventListener("change", async () => {
    clearError();
    checkbox.disabled = true;
    try {
      await request(`/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ completed: checkbox.checked }),
      });
      await loadTasks();
    } catch (error) {
      checkbox.checked = task.completed;
      checkbox.disabled = false;
      showError(`Não foi possível atualizar a tarefa. ${error.message}`);
    }
  });

  const copy = document.createElement("div");
  copy.className = "task-copy";
  const title = document.createElement("p");
  title.className = "task-title";
  title.textContent = task.title;
  const date = document.createElement("p");
  date.className = "task-date";
  date.textContent = `Criada em ${formatDate(task.created_at)}`;
  copy.append(title, date);

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete-button";
  deleteButton.type = "button";
  deleteButton.textContent = "Excluir";
  deleteButton.setAttribute("aria-label", `Excluir ${task.title}`);
  deleteButton.addEventListener("click", async () => {
    clearError();
    deleteButton.disabled = true;
    try {
      await request(`/tasks/${task.id}`, { method: "DELETE" });
      await loadTasks();
    } catch (error) {
      deleteButton.disabled = false;
      showError(`Não foi possível excluir a tarefa. ${error.message}`);
    }
  });

  item.append(checkbox, copy, deleteButton);
  return item;
}

async function loadTasks() {
  const tasks = await request("/tasks");
  taskList.replaceChildren(...tasks.map(makeTaskElement));
  const completedCount = tasks.filter((task) => task.completed).length;
  taskCount.textContent = `${completedCount} de ${tasks.length} concluídas`;
  emptyState.hidden = tasks.length > 0;
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  const submitButton = taskForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  try {
    await request("/tasks", {
      method: "POST",
      body: JSON.stringify({ title: titleInput.value.trim() }),
    });
    taskForm.reset();
    await loadTasks();
    titleInput.focus();
  } catch (error) {
    showError(`Não foi possível criar a tarefa. ${error.message}`);
  } finally {
    submitButton.disabled = false;
  }
});

loadTasks().catch((error) => {
  taskCount.textContent = "Não carregado";
  showError(`Não foi possível carregar suas tarefas. ${error.message}`);
});
