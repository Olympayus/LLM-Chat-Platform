<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
/* Global resets and base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100%;
}

/* ---- Element Plus Overrides (Linear-inspired) ---- */

/* Cards: no border, subtle shadow */
.el-card {
  border: none !important;
  box-shadow: var(--shadow-sm) !important;
  border-radius: var(--border-radius) !important;
}

.el-card__body {
  padding: 20px;
}

/* Tables: minimalist, no outer border */
.el-table {
  border: none !important;
  font-size: var(--font-size-sm);
}

.el-table th.el-table__cell {
  background-color: transparent !important;
  color: var(--color-text-muted) !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  border-bottom: 1px solid var(--color-border) !important;
  padding: 10px 12px !important;
}

.el-table td.el-table__cell {
  border-bottom: 1px solid var(--color-border-light) !important;
  padding: 10px 12px !important;
}

.el-table tbody tr:hover > td {
  background-color: var(--color-bg-hover) !important;
}

/* Buttons: more compact */
.el-button--primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.el-button--primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

/* Form: compact spacing */
.el-form-item {
  margin-bottom: 18px;
}

.el-form-item__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 500;
  padding-bottom: 4px;
}

/* Input: cleaner */
.el-input__wrapper {
  box-shadow: 0 0 0 1px var(--color-border) inset !important;
  border-radius: var(--border-radius) !important;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--color-primary) inset !important;
}

/* Tags: dot-style status */
.el-tag {
  --el-tag-border-radius: 4px;
}

/* Pagination: compact */
.el-pagination {
  font-size: var(--font-size-sm);
  padding: 12px 0;
  justify-content: flex-end;
}

/* Dialog */
.el-dialog {
  border-radius: var(--border-radius-lg) !important;
}

.el-dialog__header {
  margin-right: 0 !important;
  padding: 20px 20px 0;
}

.el-dialog__body {
  padding: 16px 20px;
}

.el-dialog__footer {
  padding: 0 20px 20px;
}

/* Switch */
.el-switch.is-checked .el-switch__core {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
}

/* Menu (sidebar) */
.el-menu {
  border-right: none !important;
}

.el-menu-item {
  font-size: 14px;
}

/* Alert */
.el-alert {
  border-radius: var(--border-radius);
}

/* Message */
.el-message {
  border: none !important;
  box-shadow: var(--shadow-md) !important;
}

/* Loading */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.7);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scr