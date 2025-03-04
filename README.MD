Django Project Version Control README

Project Overview

This Django project contains two main apps:
	1.	User System - A complete comprehensive user management system allowing admins to add, edit, and manage user permissions, and a profile page for users to update their details, including profile picture handling.
	2.	Main App - A robust app managing Decrees, Publications, Objections, and Documents in relation to registered trademarks. It includes various sections like countries, company types, document types, governments, and categories, interconnected with foreign key relationships.

Technologies Used

  •	Docker (Containerization)
	•	Django (Backend Framework)
	•	Django Tables2 (Table Views)
	•	Django Crispy Forms (Forms Rendering)
	•	PostgresSQL (Database)
	•	Bootstrap 5 + jQuery (Frontend)
	•	Javascript + AJAX (Frontend)
	•	Flatpickr (Date Picker)
	•	ReportLab (PDF Generation)
	•	Pdfjs (PDF rendering)
	•	QR Codes (Python)
	•	Plotly (Charts)
	•	Redis (Cache)
	•	Celery (Tesks)


Version History

v0.1.0 - Initial Development
	•	Initial commit of the project.
	•	Basic structure for the main app established with models for Decrees, Publications, Objections, and Documents.
	•	Bootstrap 5 added for frontend design.

v0.1.1 - Minor Fixes and Enhancements
	•	Introduced country and company type models in the main app.
	•	Basic view for Decrees and Publications added.
	•	Added pagination and table views using Django Tables2 for Decrees and Publications models.

v0.2.0 - Major Feature Additions
	•	Objection model added, with functionality to post objections on publications.
	•	Improved Decree and Publication views, with an interactive form that fetches data from the associated decree.
	•	Image rendering for Publications in the main table view.
	•	Implemented advanced search that persists across tabs.
	•	Introduced a detail function to preview document details for all models.

v0.2.1 - Minor Enhancements
	•	Improved styling for the forms and fixed minor display issues.
	•	Enhanced the interactive sidebar, ensuring it sticks across tabs and pages.
	•	Added support for Flatpickr date picker in the Decree and Publication forms and filters.

v0.3.0 - Major Features and Refinements
	•	Full interaction between models: Decrees, Publications, Objections, actions now affect each other’s statuses and permissions dynamically.
	•	Added a new model for Document Types, linked with Douments.
	•	Added the Governments model, allowing publications to reference specific government bodies.
	•	Implemented the ability to generate and download a PDF for Initial Publications using ReportLab.
	•	Introduced PostgresSQL allowing Significant performance improvements in data retrieval and form submission.

v0.3.1 - Patch Updates
	•	Implemented QR Code generation in initial publications PDF.
	•	Minor bug fixes in the Document Types management form.
	•	Improved error handling when submitting forms with missing or invalid data.
	•	Added user permissions model, ensuring more granular control for administrators and staff members.
	•	Optimized queries in the Decree and Publication models for faster page loads.

v0.3.2 - Patch Update
	•	Fixed a display bug in the Publication table view where images would not render correctly in certain cases.
	•	Added inline validation for all forms to improve user interaction.
	•	Enhanced security in the user management system by introducing additional permission checks.

v0.4.0 - Major Milestone
	•	Introduced Categories model, linked to Publications and Decrees.
	•	User system added with basic functionality for adding, editing, and deleting users.
	•	Refactored the Objection model to allow users to view their objection status via a unique code or QR code, streamlining the objection review process.
	•	Refined the Objection form’s UI for better clarity and user experience.

v0.4.1 - Minor Enhancements
	•	QR codes integrated into objections, with unique codes printed in the objection PDF using ReportLab.
	•	Fixed small UI inconsistencies in the section management interfaces.
	•	Improved accessibility and mobile responsiveness for all pages using Bootstrap 5.

v0.4.2 - Patch Update
	•	Fixed issues with image rendering in publication forms that caused broken images in the admin interface.
	•	Minor bug fixes in QR code generation logic to handle edge cases.

v0.5.0 - Major Update
	•	Interactive Sidebar revamped for better navigation and mobile support.
	•	Improved admin interface for managing and reviewing objections, with advanced filtering capabilities.
	•	Introduced a plotly chart for the index page to keep track of inserted documents.
	•	Added PDF rendering to detail views for all models.
	•	Refactored index page for a friendlier experience for the public users.

v0.5.1 - Minor Update
	•	Fixed minor issues in the user system, including permission conflicts when accessing specific pages.
	•	Introduced permissions for users with different access levels.
	•	Optimized performance for pages that load Decrees with large amounts of data.
	•	Updated Decree and Publication views to improve rendering speed and prevent timeouts.

v0.7.0 - Major Update
	•	Introduced Redis server for caching large queries and charts.
	•	Added Celery server for use in scheduled tasks.
	•	Optimized docker-compose file for a multi container application.
	•	Fully integrated user permissions system, allowing admins to set granular permissions for each user and restrict access to certain pages or actions.
	•	Introduced a fully revamped publication selection view for the public users to file an objection on. with interactive detail card for the publication as well.

v0.7.1 - Minor Update
	•	Fixed minor issues in the interface, clipping and fading objects.
	•	revamped the detail view for all models with a fresh redesigned look.
	•	fixed an intertwining permission issue preventing public objection form submission.

v1.0.0 - Stable Release
	•	Full-featured, stable release with comprehensive documentation.
	•	All models and views are fully functional.
	•	Permissions system is robust, with role-based access controls.
	•	Major features like QR code generation, advanced search, and interactive forms are fully implemented and tested.
	•	Deployed on production servers with appropriate security measures in place.

v1.1.0 - Minor Release
	•	Profile page added for users to update their details and profile pictures
	•	Refined the user profile page to allow more detailed updates (e.g., address, contact details).
	•	Enhanced performance on Publications and Decrees data retrieval, especially for large datasets.
	•	Implemented real-time updates on the objection status page.

v1.1.1 - Patch Update
	•	Fixed bugs related to QR code generation in Objections forms.
	•	Minor UI tweaks to improve mobile responsiveness.
	•	Minor bug fixes in the user system related to profile picture uploads.
	•	Optimized queries for Decrees and Publications models for better performance.

v1.1.2 - Patch Update
	•	Security patch for the User System to fix vulnerabilities in file uploads.
	•	Minor bug fix for sections management page.
	•	Optimized image rendering in Publications table view.

v1.1.3 - Final Patch for v1.1.x
	•	Fixed final bugs related to the Objection form submission and status updates.
	•	Enhanced user permissions system for more granular control over objections and publication management.