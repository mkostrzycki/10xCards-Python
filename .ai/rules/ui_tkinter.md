# UI (Tkinter/ttkbootstrap) Rules

-   **MVP Role:** Views (`infrastructure/ui/views/` within each context) are passive. They display data provided by the Presenter and delegate all user actions (events) to the Presenter.
-   **Minimal Logic:** Views contain minimal logic, primarily related to widget layout, displaying data, and binding events to Presenter methods.
-   **State:** Views DO NOT store application state. State is managed by Presenters and Domain/Application layers.
-   **Dependency Injection:** Presenters are injected into Views (usually via constructor).
-   **Event Handling:** Use dedicated View methods (e.g., `_on_save_button_click`) bound to widget events, which then call corresponding Presenter methods. Avoid complex lambdas for event handlers.
-   **Reusable Widgets:** Create reusable custom widgets (`infrastructure/ui/widgets/` or `Shared/ui/widgets/`) by inheriting from Tkinter/ttkbootstrap base classes. Define clear interfaces for interaction.
-   **Observer Pattern:** Views observe changes in data managed by the Presenter/Model. Implement this via:
    -   Presenter explicitly calling View update methods (e.g., `view.display_decks(decks)`).
    -   (Optional, if more complex state management is needed): Views subscribing to specific events/signals emitted by Presenters or Application Services.
-   **Layout:** Use Tkinter's geometry managers (`pack`, `grid`, `place`) effectively. Prefer `grid` for complex layouts.
-   **Styling:** Utilize `ttkbootstrap` themes and styles for a modern look and feel. Keep styling consistent. 