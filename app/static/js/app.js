/**
 * EduSphere AI — Core Client Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    currentTab: 'dashboard',
    searchQuery: '',
    selectedCourse: '',
    sortBy: 'created_at',
    sortOrder: 'desc',
    currentPage: 1,
    limit: 10,
    totalPages: 1,
    totalStudents: 0,
    editingStudentId: null,
    deletingStudentId: null,
    ollamaStatus: { online: false, model: null },
  };

  // DOM Elements Cache
  const elements = {
    // Nav Items
    navItems: document.querySelectorAll('.nav-item'),
    sections: document.querySelectorAll('.section-pane'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),

    // Dashboard
    kpiTotalStudents: document.getElementById('kpi-total-students'),
    kpiTotalCourses: document.getElementById('kpi-total-courses'),
    kpiRecentCount: document.getElementById('kpi-recent-count'),
    courseDistContainer: document.getElementById('course-distribution-list'),
    recentStudentsTbody: document.getElementById('recent-students-tbody'),
    btnReseedSample: document.getElementById('btn-reseed-sample'),

    // Students Table
    searchInput: document.getElementById('student-search-input'),
    courseFilterSelect: document.getElementById('course-filter-select'),
    studentsTableBody: document.getElementById('students-table-body'),
    tablePaginationWrap: document.getElementById('table-pagination-wrap'),
    paginationInfo: document.getElementById('pagination-info'),
    btnPrevPage: document.getElementById('btn-prev-page'),
    btnNextPage: document.getElementById('btn-next-page'),
    sortableHeaders: document.querySelectorAll('th.sortable'),

    // Modals
    studentModal: document.getElementById('student-form-modal'),
    studentModalTitle: document.getElementById('modal-title'),
    studentForm: document.getElementById('student-form'),
    btnGenerateId: document.getElementById('btn-generate-id'),
    btnCancelModal: document.getElementById('btn-cancel-modal'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnSaveStudent: document.getElementById('btn-save-student'),

    // Profile View Modal
    profileModal: document.getElementById('student-profile-modal'),
    btnCloseProfileModal: document.getElementById('btn-close-profile-modal'),
    btnCloseProfileBtn: document.getElementById('btn-close-profile-btn'),
    btnEditFromProfile: document.getElementById('btn-edit-from-profile'),
    profileContent: document.getElementById('profile-modal-content'),

    // Delete Confirmation Modal
    deleteModal: document.getElementById('delete-confirm-modal'),
    deleteStudentNameText: document.getElementById('delete-student-name-text'),
    btnCancelDelete: document.getElementById('btn-cancel-delete'),
    btnConfirmDelete: document.getElementById('btn-confirm-delete'),

    // AI Assistant
    aiStatusDot: document.getElementById('ai-status-dot'),
    aiStatusText: document.getElementById('ai-status-text'),
    aiHeaderModelPill: document.getElementById('ai-header-model-pill'),
    chatHistory: document.getElementById('chat-history'),
    chatInput: document.getElementById('chat-input'),
    btnSendChat: document.getElementById('btn-send-chat'),
    quickPromptPills: document.querySelectorAll('.prompt-pill'),

    // Global Action Buttons
    btnAddStudentGlobal: document.getElementById('btn-add-student-global'),
    toastContainer: document.getElementById('toast-container'),
  };

  // =========================================================
  // TOAST NOTIFICATIONS
  // =========================================================
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = '✓';
    if (type === 'error') icon = '✕';
    if (type === 'info') icon = 'ℹ';

    toast.innerHTML = `
      <span style="font-weight: 700; font-size: 1.1rem;">${icon}</span>
      <span>${escapeHtml(message)}</span>
      <button class="toast-close">&times;</button>
    `;

    elements.toastContainer.appendChild(toast);

    toast.querySelector('.toast-close').addEventListener('click', () => {
      toast.remove();
    });

    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.3s reverse forwards';
      setTimeout(() => toast.remove(), 300);
    }, 4200);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // =========================================================
  // NAVIGATION & TAB SWITCHING
  // =========================================================
  function switchTab(tabId) {
    state.currentTab = tabId;

    // Update nav links
    elements.navItems.forEach(item => {
      if (item.dataset.tab === tabId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update section visibility
    elements.sections.forEach(sec => {
      if (sec.id === `${tabId}-section`) {
        sec.classList.add('active');
      } else {
        sec.classList.remove('active');
      }
    });

    // Update Header Titles
    const titles = {
      dashboard: {
        title: 'Executive Dashboard',
        subtitle: 'Overview of student records, course distribution, and metrics',
      },
      students: {
        title: 'Student Directory',
        subtitle: 'Search, filter, update, and manage all student enrollments',
      },
      ai: {
        title: 'EduSphere AI Assistant',
        subtitle: 'Ask natural-language questions grounded directly in your student database',
      },
    };

    if (titles[tabId]) {
      elements.pageTitle.textContent = titles[tabId].title;
      elements.pageSubtitle.textContent = titles[tabId].subtitle;
    }

    // Refresh content for selected view
    if (tabId === 'dashboard') {
      loadDashboard();
    } else if (tabId === 'students') {
      loadCoursesFilter();
      loadStudents();
    } else if (tabId === 'ai') {
      checkOllamaStatus();
    }
  }

  elements.navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = item.dataset.tab;
      if (tab) switchTab(tab);
    });
  });

  // Global "Add Student" button click
  elements.btnAddStudentGlobal.addEventListener('click', () => {
    openStudentModal('create');
  });

  // =========================================================
  // DASHBOARD METRICS
  // =========================================================
  async function loadDashboard() {
    try {
      const res = await fetch('/students/stats/summary');
      if (!res.ok) throw new Error('Failed to load dashboard metrics');
      const data = await res.json();

      // Set KPIs
      elements.kpiTotalStudents.textContent = data.total_students;
      elements.kpiTotalCourses.textContent = data.courses_count;
      elements.kpiRecentCount.textContent = (data.recent_students || []).length;

      // Render Course Distribution Bars
      renderCourseDistribution(data.course_distribution || []);

      // Render Recent Students
      renderRecentStudents(data.recent_students || []);
    } catch (err) {
      console.error(err);
      showToast('Error loading dashboard statistics', 'error');
    }
  }

  function renderCourseDistribution(dist) {
    if (!dist || dist.length === 0) {
      elements.courseDistContainer.innerHTML = `
        <div style="text-align: center; color: var(--text-muted); padding: 20px;">
          No student course records yet.
        </div>
      `;
      return;
    }

    elements.courseDistContainer.innerHTML = dist.map(item => `
      <div class="course-dist-item">
        <div class="course-dist-label">
          <span>${escapeHtml(item.course)}</span>
          <span class="course-dist-meta"><strong>${item.count}</strong> students (${item.percentage}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-bar-fill" style="width: ${Math.max(item.percentage, 4)}%"></div>
        </div>
      </div>
    `).join('');
  }

  function renderRecentStudents(students) {
    if (!students || students.length === 0) {
      elements.recentStudentsTbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">
            No students registered yet. Click <strong>Add Student</strong> to begin.
          </td>
        </tr>
      `;
      return;
    }

    elements.recentStudentsTbody.innerHTML = students.map(s => `
      <tr>
        <td>
          <div class="student-cell">
            <div class="avatar">${getInitials(s.full_name)}</div>
            <div class="student-meta">
              <div class="student-name">${escapeHtml(s.full_name)}</div>
              <div class="student-id-sub">${escapeHtml(s.student_id)}</div>
            </div>
          </div>
        </td>
        <td>
          <span class="badge ${s.course ? 'badge-teal' : 'badge-gray'}">
            ${escapeHtml(s.course || 'Unassigned')}
          </span>
        </td>
        <td>${formatDate(s.date_of_birth)}</td>
        <td>${escapeHtml(s.email || s.phone || '—')}</td>
        <td>
          <div class="row-actions">
            <button class="action-btn" title="View Profile" onclick="window.viewStudentProfile('${s.student_id}')">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
            <button class="action-btn" title="Edit Student" onclick="window.editStudent('${s.student_id}')">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  // Reseed Sample Data Button
  elements.btnReseedSample.addEventListener('click', async () => {
    if (!confirm('This will repopulate the database with realistic sample student records. Continue?')) return;
    try {
      const res = await fetch('/api/seed?reset=true', { method: 'POST' });
      if (!res.ok) throw new Error('Reseed failed');
      const data = await res.json();
      showToast(data.message, 'success');
      loadDashboard();
      if (state.currentTab === 'students') loadStudents();
    } catch (err) {
      showToast('Failed to seed records: ' + err.message, 'error');
    }
  });

  // =========================================================
  // STUDENTS LIST & TABLE
  // =========================================================
  async function loadCoursesFilter() {
    try {
      const res = await fetch('/students/meta/courses');
      if (!res.ok) return;
      const courses = await res.json();

      const currentVal = elements.courseFilterSelect.value;
      elements.courseFilterSelect.innerHTML = `
        <option value="">All Courses</option>
        ${courses.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('')}
      `;
      elements.courseFilterSelect.value = currentVal;
    } catch (e) {
      console.warn('Could not load course list for filter', e);
    }
  }

  async function loadStudents() {
    elements.studentsTableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 40px;">
          <div class="spinner" style="border-top-color: var(--teal-primary); border-color: rgba(13,148,136,0.2);"></div>
          <div style="margin-top: 8px; color: var(--text-muted); font-size: 0.85rem;">Loading student records...</div>
        </td>
      </tr>
    `;

    try {
      const skip = (state.currentPage - 1) * state.limit;
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: state.limit.toString(),
        sort_by: state.sortBy,
        order: state.sortOrder,
      });

      if (state.searchQuery.trim()) {
        params.append('search', state.searchQuery.trim());
      }
      if (state.selectedCourse.trim()) {
        params.append('course', state.selectedCourse.trim());
      }

      const res = await fetch(`/students?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load students');
      const data = await res.json();

      state.totalStudents = data.total;
      state.totalPages = data.total_pages;

      renderStudentsTable(data.items);
      updatePaginationControls();
    } catch (err) {
      console.error(err);
      elements.studentsTableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 40px; color: var(--coral-danger);">
            Failed to load students. Please refresh or check server connection.
          </td>
        </tr>
      `;
    }
  }

  function renderStudentsTable(students) {
    if (!students || students.length === 0) {
      elements.studentsTableBody.innerHTML = `
        <tr>
          <td colspan="6">
            <div class="empty-state">
              <div class="empty-icon">
                <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
              </div>
              <h4>No Students Found</h4>
              <p>No student records match your current search or course filter criteria.</p>
              <button class="btn btn-outline-teal btn-sm" onclick="window.clearFilters()">Clear Filters</button>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    elements.studentsTableBody.innerHTML = students.map(s => `
      <tr>
        <td>
          <div class="student-cell">
            <div class="avatar">${getInitials(s.full_name)}</div>
            <div class="student-meta">
              <div class="student-name">${escapeHtml(s.full_name)}</div>
              <div class="student-id-sub">${escapeHtml(s.student_id)}</div>
            </div>
          </div>
        </td>
        <td>
          <span class="badge ${s.course ? 'badge-teal' : 'badge-gray'}">
            ${escapeHtml(s.course || 'Unassigned')}
          </span>
        </td>
        <td>${formatDate(s.date_of_birth)}</td>
        <td>
          <div style="font-size: 0.85rem;">
            ${s.email ? `<div><a href="mailto:${escapeHtml(s.email)}" style="color: var(--teal-primary); text-decoration: none;">${escapeHtml(s.email)}</a></div>` : ''}
            ${s.phone ? `<div style="color: var(--text-muted); font-size: 0.78rem;">${escapeHtml(s.phone)}</div>` : ''}
          </div>
        </td>
        <td>${formatDate(s.enrollment_date)}</td>
        <td>
          <div class="row-actions">
            <button class="action-btn" title="View Profile" onclick="window.viewStudentProfile('${s.student_id}')">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
            <button class="action-btn" title="Edit Student" onclick="window.editStudent('${s.student_id}')">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="action-btn delete-btn" title="Delete Student" onclick="window.confirmDeleteStudent('${s.student_id}', '${escapeHtml(s.full_name)}')">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  function updatePaginationControls() {
    const start = state.totalStudents === 0 ? 0 : (state.currentPage - 1) * state.limit + 1;
    const end = Math.min(state.currentPage * state.limit, state.totalStudents);
    elements.paginationInfo.textContent = `Showing ${start}–${end} of ${state.totalStudents} students`;

    elements.btnPrevPage.disabled = state.currentPage <= 1;
    elements.btnNextPage.disabled = state.currentPage >= state.totalPages;
  }

  // Search input debouncer
  let searchTimeout;
  elements.searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.searchQuery = e.target.value;
      state.currentPage = 1;
      loadStudents();
    }, 300);
  });

  // Course filter
  elements.courseFilterSelect.addEventListener('change', (e) => {
    state.selectedCourse = e.target.value;
    state.currentPage = 1;
    loadStudents();
  });

  // Pagination buttons
  elements.btnPrevPage.addEventListener('click', () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      loadStudents();
    }
  });

  elements.btnNextPage.addEventListener('click', () => {
    if (state.currentPage < state.totalPages) {
      state.currentPage++;
      loadStudents();
    }
  });

  // Sorting
  elements.sortableHeaders.forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (state.sortBy === col) {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        state.sortBy = col;
        state.sortOrder = 'asc';
      }
      loadStudents();
    });
  });

  window.clearFilters = () => {
    elements.searchInput.value = '';
    elements.courseFilterSelect.value = '';
    state.searchQuery = '';
    state.selectedCourse = '';
    state.currentPage = 1;
    loadStudents();
  };

  // =========================================================
  // ADD & EDIT STUDENT MODAL
  // =========================================================
  function openStudentModal(mode = 'create', studentData = null) {
    clearFormErrors();
    elements.studentForm.reset();

    const studentIdInput = document.getElementById('field-student-id');
    const enrollmentInput = document.getElementById('field-enrollment-date');

    if (mode === 'create') {
      state.editingStudentId = null;
      elements.studentModalTitle.textContent = 'Add New Student';
      studentIdInput.disabled = false;
      elements.btnGenerateId.style.display = 'inline-flex';
      enrollmentInput.value = new Date().toISOString().split('T')[0];
    } else {
      state.editingStudentId = studentData.student_id;
      elements.studentModalTitle.textContent = `Edit Student — ${studentData.full_name}`;
      studentIdInput.disabled = true;
      elements.btnGenerateId.style.display = 'none';

      // Pre-fill form
      studentIdInput.value = studentData.student_id;
      document.getElementById('field-full-name').value = studentData.full_name;
      document.getElementById('field-dob').value = studentData.date_of_birth;
      document.getElementById('field-email').value = studentData.email || '';
      document.getElementById('field-phone').value = studentData.phone || '';
      document.getElementById('field-course').value = studentData.course || '';
      document.getElementById('field-address').value = studentData.address || '';
      document.getElementById('field-enrollment-date').value = studentData.enrollment_date || '';
    }

    elements.studentModal.classList.add('active');
  }

  function closeStudentModal() {
    elements.studentModal.classList.remove('active');
  }

  elements.btnCancelModal.addEventListener('click', closeStudentModal);
  elements.btnCloseModal.addEventListener('click', closeStudentModal);

  // Generate ID helper
  elements.btnGenerateId.addEventListener('click', () => {
    const year = new Date().getFullYear();
    const rand = Math.floor(100 + Math.random() * 900);
    document.getElementById('field-student-id').value = `STU-${year}-${rand}`;
  });

  // Form Submission
  elements.studentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearFormErrors();

    const studentId = document.getElementById('field-student-id').value.trim().toUpperCase();
    const fullName = document.getElementById('field-full-name').value.trim();
    const dob = document.getElementById('field-dob').value;
    const email = document.getElementById('field-email').value.trim();
    const phone = document.getElementById('field-phone').value.trim();
    const course = document.getElementById('field-course').value.trim();
    const address = document.getElementById('field-address').value.trim();
    const enrollmentDate = document.getElementById('field-enrollment-date').value;

    // Client Validation
    let hasError = false;

    if (!state.editingStudentId && !studentId) {
      showFieldError('field-student-id', 'Student ID is required');
      hasError = true;
    }

    if (!fullName || fullName.length < 2) {
      showFieldError('field-full-name', 'Full name must be at least 2 characters');
      hasError = true;
    }

    if (!dob) {
      showFieldError('field-dob', 'Date of birth is required');
      hasError = true;
    } else {
      const birthDate = new Date(dob);
      const today = new Date();
      if (birthDate >= today) {
        showFieldError('field-dob', 'Date of birth must be in the past');
        hasError = true;
      }
    }

    if (!email && !phone) {
      showFieldError('field-email', 'Provide at least an email or phone number');
      showFieldError('field-phone', 'Provide at least an email or phone number');
      hasError = true;
    }

    if (email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        showFieldError('field-email', 'Please enter a valid email address');
        hasError = true;
      }
    }

    if (hasError) return;

    const payload = {
      full_name: fullName,
      date_of_birth: dob,
      email: email || null,
      phone: phone || null,
      course: course || null,
      address: address || null,
      enrollment_date: enrollmentDate || null,
    };

    if (!state.editingStudentId) {
      payload.student_id = studentId;
    }

    // Set saving spinner
    elements.btnSaveStudent.disabled = true;
    elements.btnSaveStudent.innerHTML = `<span class="spinner"></span> Saving...`;

    try {
      let res;
      if (state.editingStudentId) {
        // PUT update
        res = await fetch(`/students/${encodeURIComponent(state.editingStudentId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        // POST create
        res = await fetch('/students', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      const resData = await res.json();

      if (!res.ok) {
        if (res.status === 409) {
          showFieldError('field-student-id', resData.detail || 'Student ID already exists');
        } else if (res.status === 422) {
          const detailMsg = Array.isArray(resData.errors) ? resData.errors.join(', ') : resData.message;
          showToast(detailMsg || 'Validation error', 'error');
        } else {
          showToast(resData.detail || 'Failed to save student', 'error');
        }
        return;
      }

      showToast(
        state.editingStudentId ? 'Student profile updated successfully!' : 'Student registered successfully!',
        'success'
      );
      closeStudentModal();
      loadStudents();
      loadDashboard();
      loadCoursesFilter();
    } catch (err) {
      console.error(err);
      showToast('Network error while saving student', 'error');
    } finally {
      elements.btnSaveStudent.disabled = false;
      elements.btnSaveStudent.innerHTML = `Save Student Record`;
    }
  });

  function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) field.classList.add('error');
    const errBox = document.getElementById(`${fieldId}-error`);
    if (errBox) {
      errBox.textContent = message;
      errBox.classList.add('visible');
    }
  }

  function clearFormErrors() {
    document.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(el => el.classList.remove('error'));
    document.querySelectorAll('.field-error-msg').forEach(el => {
      el.textContent = '';
      el.classList.remove('visible');
    });
  }

  // =========================================================
  // STUDENT PROFILE VIEW MODAL
  // =========================================================
  window.viewStudentProfile = async (studentId) => {
    try {
      const res = await fetch(`/students/${encodeURIComponent(studentId)}`);
      if (!res.ok) throw new Error('Student record not found');
      const s = await res.json();

      const age = calculateAge(s.date_of_birth);

      elements.profileContent.innerHTML = `
        <div class="profile-hero">
          <div class="profile-avatar-lg">${getInitials(s.full_name)}</div>
          <div class="profile-title">
            <h4>${escapeHtml(s.full_name)}</h4>
            <div style="display: flex; gap: 8px; margin-top: 6px; align-items: center;">
              <span class="badge badge-teal" style="font-family: monospace;">ID: ${escapeHtml(s.student_id)}</span>
              <span class="badge ${s.course ? 'badge-sky' : 'badge-gray'}">${escapeHtml(s.course || 'No Course')}</span>
            </div>
          </div>
        </div>

        <div class="profile-info-grid">
          <div class="profile-info-item">
            <div class="item-label">Date of Birth & Age</div>
            <div class="item-val">${formatDate(s.date_of_birth)} (${age} years old)</div>
          </div>
          <div class="profile-info-item">
            <div class="item-label">Enrollment Date</div>
            <div class="item-val">${formatDate(s.enrollment_date)}</div>
          </div>
          <div class="profile-info-item">
            <div class="item-label">Email Address</div>
            <div class="item-val">
              ${s.email ? `<a href="mailto:${escapeHtml(s.email)}" style="color: var(--teal-primary);">${escapeHtml(s.email)}</a>` : '—'}
            </div>
          </div>
          <div class="profile-info-item">
            <div class="item-label">Phone Number</div>
            <div class="item-val">
              ${s.phone ? `<a href="tel:${escapeHtml(s.phone)}" style="color: var(--teal-primary);">${escapeHtml(s.phone)}</a>` : '—'}
            </div>
          </div>
          <div class="profile-info-item" style="grid-column: span 2;">
            <div class="item-label">Residential Address</div>
            <div class="item-val">${escapeHtml(s.address || 'No address registered')}</div>
          </div>
          <div class="profile-info-item">
            <div class="item-label">Created At</div>
            <div class="item-val">${formatDateTime(s.created_at)}</div>
          </div>
          <div class="profile-info-item">
            <div class="item-label">Last Updated</div>
            <div class="item-val">${formatDateTime(s.updated_at)}</div>
          </div>
        </div>
      `;

      elements.btnEditFromProfile.onclick = () => {
        elements.profileModal.classList.remove('active');
        window.editStudent(s.student_id);
      };

      elements.profileModal.classList.add('active');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  elements.btnCloseProfileModal.addEventListener('click', () => {
    elements.profileModal.classList.remove('active');
  });
  elements.btnCloseProfileBtn.addEventListener('click', () => {
    elements.profileModal.classList.remove('active');
  });

  // Edit Student Row Trigger
  window.editStudent = async (studentId) => {
    try {
      const res = await fetch(`/students/${encodeURIComponent(studentId)}`);
      if (!res.ok) throw new Error('Student record not found');
      const student = await res.json();
      openStudentModal('edit', student);
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // =========================================================
  // DELETE CONFIRMATION DIALOG
  // =========================================================
  window.confirmDeleteStudent = (studentId, studentName) => {
    state.deletingStudentId = studentId;
    elements.deleteStudentNameText.textContent = `Are you sure you want to permanently delete student "${studentName}" (ID: ${studentId})? This action cannot be reversed.`;
    elements.deleteModal.classList.add('active');
  };

  elements.btnCancelDelete.addEventListener('click', () => {
    elements.deleteModal.classList.remove('active');
    state.deletingStudentId = null;
  });

  elements.btnConfirmDelete.addEventListener('click', async () => {
    if (!state.deletingStudentId) return;

    elements.btnConfirmDelete.disabled = true;
    elements.btnConfirmDelete.innerHTML = `<span class="spinner"></span> Deleting...`;

    try {
      const res = await fetch(`/students/${encodeURIComponent(state.deletingStudentId)}`, {
        method: 'DELETE',
      });
      const data = await res.json();

      if (!res.ok) {
        showToast(data.detail || 'Failed to delete student', 'error');
        return;
      }

      showToast(data.message || 'Student deleted successfully', 'success');
      elements.deleteModal.classList.remove('active');
      state.deletingStudentId = null;
      loadStudents();
      loadDashboard();
      loadCoursesFilter();
    } catch (err) {
      showToast('Error during deletion', 'error');
    } finally {
      elements.btnConfirmDelete.disabled = false;
      elements.btnConfirmDelete.innerHTML = `Delete Record`;
    }
  });

  // =========================================================
  // AI ASSISTANT CHAT
  // =========================================================
  async function checkOllamaStatus() {
    try {
      const res = await fetch('/api/ai/status');
      if (!res.ok) throw new Error('AI status unreachable');
      const data = await res.json();

      state.ollamaStatus.online = data.ollama_available;
      state.ollamaStatus.model = data.configured_model;

      if (data.ollama_available) {
        elements.aiStatusDot.className = 'status-dot online';
        elements.aiStatusText.textContent = `Ollama: Active (${data.configured_model})`;
        elements.aiHeaderModelPill.className = 'ai-model-pill active';
        elements.aiHeaderModelPill.textContent = `Ollama Online (${data.configured_model})`;
      } else {
        elements.aiStatusDot.className = 'status-dot';
        elements.aiStatusText.textContent = 'Grounded DB Engine (Ollama Offline)';
        elements.aiHeaderModelPill.className = 'ai-model-pill offline';
        elements.aiHeaderModelPill.textContent = 'Grounded Mode (Ollama Offline)';
      }
    } catch (e) {
      elements.aiStatusDot.className = 'status-dot';
      elements.aiStatusText.textContent = 'Local Grounded Engine';
      elements.aiHeaderModelPill.className = 'ai-model-pill offline';
      elements.aiHeaderModelPill.textContent = 'Offline Engine Active';
    }
  }

  async function sendChatMessage(queryText) {
    const text = (queryText || elements.chatInput.value).trim();
    if (!text) return;

    elements.chatInput.value = '';

    // Append User Message
    appendChatMessage('user', text);

    // Append Loading Assistant Message
    const loadingId = 'ai-loading-' + Date.now();
    appendLoadingBubble(loadingId);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      removeLoadingBubble(loadingId);

      if (!res.ok) {
        appendChatMessage('assistant', `⚠️ **Error:** ${data.detail || 'Unable to process query.'}`);
        return;
      }

      appendChatMessage('assistant', data.answer, data.source);
    } catch (err) {
      removeLoadingBubble(loadingId);
      appendChatMessage('assistant', '⚠️ **Network Error:** Could not contact the EduSphere AI backend.');
    }
  }

  function appendChatMessage(sender, content, source = '') {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;

    const formattedContent = renderMarkdown(content);

    let avatarSvg = sender === 'user'
      ? `<div class="avatar" style="background-color: var(--teal-light); color: var(--teal-primary);">You</div>`
      : `<div class="avatar" style="background-color: var(--mint-light); color: var(--mint-primary);">AI</div>`;

    let badge = '';
    if (sender === 'assistant' && source) {
      const isOllama = source === 'ollama';
      badge = `<div style="font-size: 0.7rem; color: var(--text-light); margin-top: 6px;">
        ${isOllama ? '✨ Generated via Ollama LLM' : '🛡️ Verified via SQLite Grounded Rules'}
      </div>`;
    }

    msgDiv.innerHTML = `
      ${avatarSvg}
      <div class="chat-bubble">
        ${formattedContent}
        ${badge}
      </div>
    `;

    elements.chatHistory.appendChild(msgDiv);
    elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
  }

  function appendLoadingBubble(id) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message assistant';
    msgDiv.id = id;
    msgDiv.innerHTML = `
      <div class="avatar" style="background-color: var(--mint-light); color: var(--mint-primary);">AI</div>
      <div class="chat-bubble" style="display: flex; align-items: center; gap: 8px;">
        <span class="spinner" style="border-top-color: var(--teal-primary); border-color: rgba(13,148,136,0.2);"></span>
        <span style="color: var(--text-muted); font-size: 0.85rem;">Retrieving records and generating grounded response...</span>
      </div>
    `;
    elements.chatHistory.appendChild(msgDiv);
    elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
  }

  function removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // Quick prompt pills
  elements.quickPromptPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const q = pill.dataset.query || pill.textContent.replace(/^💬\s*/, '').trim();
      sendChatMessage(q);
    });
  });

  elements.btnSendChat.addEventListener('click', () => sendChatMessage());
  elements.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendChatMessage();
    }
  });

  // Basic safe markdown parser for chat answers
  function renderMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold & Italics
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

    // Inline code
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

    // Blockquotes
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');

    // Bullet lists
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');

    // Line breaks
    html = html.replace(/\n\n/gim, '</p><p>');
    html = html.replace(/\n/gim, '<br>');

    return `<p>${html}</p>`;
  }

  // =========================================================
  // UTILITY HELPERS
  // =========================================================
  function getInitials(name) {
    if (!name) return 'ED';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  }

  function formatDateTime(dtStr) {
    if (!dtStr) return '—';
    try {
      const d = new Date(dtStr);
      return d.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dtStr;
    }
  }

  function calculateAge(dobStr) {
    if (!dobStr) return 0;
    const dob = new Date(dobStr);
    const today = new Date();
    let age = today.getFullYear() - dob.getFullYear();
    const m = today.getMonth() - dob.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
      age--;
    }
    return age;
  }

  // Initial Load
  switchTab('dashboard');
  checkOllamaStatus();
});
