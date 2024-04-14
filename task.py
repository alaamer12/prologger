class Task:
    def __init__(self, title, description, due_date, priority, category):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.category = category
        self.completed = False

    def __str__(self):
        status = "Completed" if self.completed else "Not Completed"
        return f"{self.title}\nDescription: {self.description}\nDue Date: {self.due_date}\nPriority: {self.priority}\nCategory: {self.category}\nStatus: {status}\n"


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def mark_task_as_completed(self, task_title):
        for task in self.tasks:
            if task.title == task_title:
                task.completed = True

    def get_all_tasks(self):
        return self.tasks


def main():
    task_manager = TaskManager()

    while True:
        print("\nTask Manager Menu:")
        print("1. Add Task")
        print("2. Mark Task as Completed")
        print("3. View All Tasks")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            due_date = input("Enter due date (YYYY-MM-DD): ")
            priority = input("Enter priority (High/Medium/Low): ")
            category = input("Enter category: ")
            task = Task(title, description, due_date, priority, category)
            task_manager.add_task(task)
            print("Task added successfully!")
        elif choice == "2":
            task_title = input("Enter the title of the task to mark as completed: ")
            task_manager.mark_task_as_completed(task_title)
            print("Task marked as completed!")
        elif choice == "3":
            tasks = task_manager.get_all_tasks()
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    print(task)
        elif choice == "4":
            print("Exiting Task Manager.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
