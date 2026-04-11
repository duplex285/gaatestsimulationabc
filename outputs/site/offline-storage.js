/**
 * IndexedDB persistence for ABC Assessment.
 * Stores in-progress responses, completed results, and Bayesian profile state.
 * All functions return Promises. Exported via window.ABCOfflineStorage.
 */

(function() {
    'use strict';

    var DB_NAME = 'abc_assessment_db';
    var DB_VERSION = 1;
    var db = null;

    function openDB() {
        if (db) return Promise.resolve(db);
        return new Promise(function(resolve, reject) {
            var request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = function(event) {
                var database = event.target.result;
                if (!database.objectStoreNames.contains('responses')) {
                    database.createObjectStore('responses', { keyPath: 'timestamp' });
                }
                if (!database.objectStoreNames.contains('results')) {
                    database.createObjectStore('results', { keyPath: 'timestamp' });
                }
                if (!database.objectStoreNames.contains('profile')) {
                    database.createObjectStore('profile', { keyPath: 'key' });
                }
            };

            request.onsuccess = function(event) {
                db = event.target.result;
                resolve(db);
            };

            request.onerror = function(event) {
                reject(event.target.error);
            };
        });
    }

    /**
     * Save in-progress assessment responses (auto-save as user answers).
     */
    function saveInProgress(tier, responses) {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('responses', 'readwrite');
                var store = tx.objectStore('responses');
                // Use a fixed key so we always overwrite the single in-progress record
                store.put({
                    timestamp: 'in_progress',
                    tier: tier,
                    responses: responses,
                    completed: false,
                    savedAt: Date.now()
                });
                tx.oncomplete = function() { resolve(); };
                tx.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Load in-progress assessment (if any).
     */
    function loadInProgress() {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('responses', 'readonly');
                var store = tx.objectStore('responses');
                var request = store.get('in_progress');
                request.onsuccess = function() {
                    resolve(request.result || null);
                };
                request.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Clear in-progress data after submission.
     */
    function clearInProgress() {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('responses', 'readwrite');
                var store = tx.objectStore('responses');
                store.delete('in_progress');
                tx.oncomplete = function() { resolve(); };
                tx.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Save a completed assessment result.
     */
    function saveResult(result) {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('results', 'readwrite');
                var store = tx.objectStore('results');
                var entry = Object.assign({}, result, { timestamp: Date.now() });
                store.put(entry);
                tx.oncomplete = function() { resolve(); };
                tx.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Retrieve all past results, sorted by timestamp ascending.
     */
    function getResultHistory() {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('results', 'readonly');
                var store = tx.objectStore('results');
                var request = store.getAll();
                request.onsuccess = function() {
                    var results = request.result || [];
                    results.sort(function(a, b) { return a.timestamp - b.timestamp; });
                    resolve(results);
                };
                request.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Save Bayesian scorer state (posteriors) for persistence across sessions.
     */
    function saveBayesianState(state) {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('profile', 'readwrite');
                var store = tx.objectStore('profile');
                store.put({ key: 'current', state: state, savedAt: Date.now() });
                tx.oncomplete = function() { resolve(); };
                tx.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    /**
     * Load Bayesian scorer state from previous sessions.
     */
    function loadBayesianState() {
        return openDB().then(function(database) {
            return new Promise(function(resolve, reject) {
                var tx = database.transaction('profile', 'readonly');
                var store = tx.objectStore('profile');
                var request = store.get('current');
                request.onsuccess = function() {
                    var record = request.result;
                    resolve(record ? record.state : null);
                };
                request.onerror = function(event) { reject(event.target.error); };
            });
        });
    }

    // Export
    window.ABCOfflineStorage = {
        saveInProgress: saveInProgress,
        loadInProgress: loadInProgress,
        clearInProgress: clearInProgress,
        saveResult: saveResult,
        getResultHistory: getResultHistory,
        saveBayesianState: saveBayesianState,
        loadBayesianState: loadBayesianState
    };
})();
