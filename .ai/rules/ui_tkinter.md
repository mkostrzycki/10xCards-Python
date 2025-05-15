# UI (Tkinter/ttkbootstrap) Rules

-   **MVP Role:** Views (`infrastructure/ui/views/` within each context) are passive. They display data provided by the Presenter and delegate all user actions (events) to the Presenter.
-   **View Interfaces:** Presenters communicate with Views through well-defined View Interfaces (e.g., using `typing.Protocol` or `abc.ABC`). Views implement these interfaces, allowing presenters to call update methods (e.g., `view.display_items(items)`).
-   **Minimal Logic:** Views contain minimal logic, primarily related to widget layout, displaying data, and binding events to Presenter methods.
-   **State:** Views DO NOT store application state. State is managed by Presenters and Domain/Application layers.
-   **Dependency Injection:** Presenters are injected into Views (usually via constructor).
-   **Event Handling:** Use dedicated View methods (e.g., `_on_save_button_click`) bound to widget events, which then call corresponding Presenter methods. Avoid complex lambdas for event handlers.
-   **Reusable Components & Centralization:** Create reusable custom widgets by inheriting from Tkinter/ttkbootstrap base classes. Actively identify and centralize common UI patterns (e.g., `ConfirmationDialog`, `BaseDialog`, `GenericTableWidget`) in `Shared/ui/widgets/` to ensure consistency and reduce duplication. Define clear interfaces for interaction.
-   **Dialog Coordination:** Dialog lifecycle (instantiation, display) and result handling should be coordinated by the responsible Presenter. Views may request dialogs, but Presenters manage the flow and outcome.
-   **Layout:** Use Tkinter's geometry managers (`pack`, `grid`, `place`) effectively. Prefer `grid` for complex layouts.
-   **Styling & Theming:** Prioritize predefined `ttkbootstrap` styles (e.g., `primary.TButton`, `h1.TLabel`) over custom, hardcoded styling (colors, fonts) to ensure consistent appearance and full compatibility with dynamic theme changes (FR-063). All custom widgets must be 'themable'.
-   **Button Order:** In dialogs and forms, place the primary action button (e.g., "Save", "OK", "Submit") on the right side and secondary/cancel actions to its left. This maintains consistency with common UI patterns.