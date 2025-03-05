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

v0.1.6 - Minor Fixes and Enhancements
	•	Introduced country and company type models in the main app.
	•	Basic view for Decrees and Publications added.
	•	Added pagination and table views using Django Tables2 for Decrees and Publications models.

v0.2.1 - Major Feature Additions
	•	Objection model added, with functionality to post objections on publications.
	•	Improved Decree and Publication views, with an interactive form that fetches data from the associated decree.
	•	Image rendering for Publications in the main table view.
	•	Implemented advanced search that persists across tabs.
	•	Introduced a detail function to preview document details for all models.

v0.2.4 - Minor Enhancements
	•	Improved styling for the forms and fixed minor display issues.
	•	Enhanced the interactive sidebar, ensuring it sticks across tabs and pages.
	•	Added support for Flatpickr date picker in the Decree and Publication forms and filters.

v0.3.0 - Major Milestone
	•	Full interaction between models: Decrees, Publications, Objections, actions now affect each other’s statuses and permissions dynamically.
	•	Added new models for Document Types, Company Types, Countries, and Decree Catagories, and linked them with related models.
	•	Added the optional Governments model, allowing publications to be linked to specific government bodies.
	•	Implemented the ability to generate and download a PDF for Initial Publications using ReportLab.
	•	Introduced PostgresSQL allowing Significant performance improvements in data retrieval and form submission.
	•	Enhanced the main UI and relied more heavily on Bootstrap5 and further enhanced visuals.

v0.3.5 - Major Features and Refinements
	•	Implemented QR Code generation in initial publications PDF.
	•	Minor bug fixes in the Document Types management form.
	•	Improved error handling when submitting forms with missing or invalid data.
	•	Added user permissions model, ensuring more granular control for administrators and staff members.
	•	Optimized queries in the Decree and Publication models for faster page loads.

v0.3.8 - Patch Update
	•	Fixed a display bug in the Publication table view where images would not render correctly in certain cases.
	•	Added inline validation for all forms to improve user interaction.
	•	Enhanced security in the user management system by introducing additional permission checks.

v0.4.2 - Minor Update
	•	Introduced Categories model, linked to Publications and Decrees.
	•	User system added with basic functionality for adding, editing, and deleting users.
	•	Refactored the Objection model to allow users to view their objection status via a unique code, streamlining the objection review process.
	•	Refined the Objection form’s UI for better clarity and user experience.

v0.4.4 - Minor Enhancements
	•	QR codes integrated into objections, with unique codes printed in the objection PDF using ReportLab.
	•	Fixed small UI inconsistencies in the section management interfaces.
	•	Improved accessibility and mobile responsiveness for all pages using Bootstrap 5.

v0.4.6 - Patch Update
	•	Fixed issues with image rendering in publication forms that caused broken images in the admin interface.
	•	Minor bug fixes in QR code generation logic to handle edge cases.

v0.5.1 - Major Update
	•	Interactive Sidebar revamped for better navigation and mobile support.
	•	Improved admin interface for managing and reviewing all models, with advanced filtering capabilities.
	•	Introduced a plotly chart for the index page to keep track of inserted documents.
	•	Added PDF rendering to detail views for all models.
	•	Refactored index page for a friendlier experience for the public users.

v0.5.5 - Minor Update
	•	Fixed minor issues in the user system, including permission conflicts when accessing specific pages.
	•	Introduced permissions for users with different access levels.
	•	Optimized performance for pages that load Decrees with large amounts of data.
	•	Updated Decree and Publication views to improve rendering speed and prevent timeouts.

v0.6.0 - Major Update
	•	Introduced Redis server for caching large queries and charts.
	•	Added Celery server for use in scheduled tasks.
	•	Optimized docker-compose file for a multi container application.
	•	Fully integrated user permissions system, allowing admins to set granular permissions for each user and restrict access to certain pages or actions.
	•	Introduced a fully revamped publication selection view for the public users to file an objection on. with interactive detail card for the publication as well.

v0.6.4 - Patch update
	•	Fixed minor issues in the interface, clipping and fading objects.
	•	revamped the detail view for all models with a fresh redesigned look.
	•	fixed an intertwining permission issue preventing public objection form submission.

v0.6.9 - Major Update
	•	Initial alpha release for testing, added comprehensive documentation.
	•	All models and views are fully functional.
	•	Permissions system is robust, with role-based access controls.
	•	Major features like QR code generation, advanced search, and interactive forms are fully implemented and tested.
	•	Deployed on production servers with appropriate security measures in place.

v0.7.3 - Minor Update
	•	Profile page added for users to update their details
	•	Refined the user profile page to allow more detailed updates (e.g., address, contact details).
	•	Enhanced performance on Publications and Decrees data retrieval, especially for large datasets.
	•	Implemented real-time updates on the objection status page.

v0.7.6 - Patch Update
	•	Security patch for the User System to fix vulnerabilities in file uploads.
	•	Minor bug fix for sections management page.
	•	Optimized image rendering in Publications table view.

v0.8.0 - Minor Fixes and Enhancements
	•	Fixed bugs related to QR code generation in Objections forms.
	•	Minor UI tweaks to improve mobile responsiveness.
	•	Minor bug fixes in the user system related to permissions and details.
	•	Optimized queries for Decrees and Publications models for better performance.

v0.8.2 - Patch Update
	•	Fixed final bugs related to the Objection form submission and status updates.
	•	Enhanced user permissions system for more granular control over objections and publication management.

v0.8.7 - Major Update
	•	Added the ability for the user to add a profile picture from profile page.
	•	Fixed a bug with migrations not being applied correctly upon first deployment.
	•	Separated the web application from the underlying python container in Docker-compose file.
	•	Refined the Docker-compose file to reflect real-time changes using a volume within base image.
	•	Added soft-deletion permissions to superuser and made them get logged in the user log.

v0.9.1 - Patch Update
	•	Fixed media and staticfiles permission issues inside the container.
	•	Enhanced the User creation form and added further security measures.
	•	Fixed the category not being submitted correctly in the new publication form.

v0.9.7 - Major Features and Refinements
	•	Changed the Decree model to be accessable for view by the public.
	•	Fixed permission issues with decree model and logging.
	•	Introduced a new view for decrees for public view and download of related decrees.
	•	Enhanced the overall colors and shadows of cards and their content.
	•	Added a link to download objection pdf to the public objection tracking modal.
	•	Enhanced the number fields logic on Publications and Objections.

v0.9.9 - Patch Update
	•	Fixed filters on the objection publication pick interface.
	•	Fixed some clipping and out of order visuals in forms and table views.

v1.0.0 - Stable Release
	•	Full-featured stable release.

