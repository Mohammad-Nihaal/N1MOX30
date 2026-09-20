import { useEffect, useState } from "react";
import {
  AlertCircle,
  CalendarDays,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";

import api from "../api/client";


function Schedules() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    schedule_type: "daily",
    hour: "9",
    minute: "0",
  });


  async function loadSchedules() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/schedules");

      setSchedules(
        Array.isArray(response.data)
          ? response.data
          : response.data.schedules || []
      );
    } catch (error) {
      console.error("Schedule loading error:", error);

      setError(
        error?.response?.data?.detail ||
          "Unable to load schedules."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadSchedules();
  }, []);


  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }


  async function createSchedule(event) {
    event.preventDefault();

    if (!formData.name.trim()) {
      setError("Please enter a schedule name.");
      return;
    }

    try {
      setCreating(true);
      setError("");
      setSuccess("");

      await api.post("/schedules", {
        name: formData.name.trim(),
        schedule_type: formData.schedule_type,
        hour: Number(formData.hour),
        minute: Number(formData.minute),
      });

      setSuccess("Schedule created successfully.");

      setFormData({
        name: "",
        schedule_type: "daily",
        hour: "9",
        minute: "0",
      });

      await loadSchedules();
    } catch (error) {
      console.error("Schedule creation error:", error);

      setError(
        error?.response?.data?.detail ||
          "Unable to create schedule."
      );
    } finally {
      setCreating(false);
    }
  }


  async function deleteSchedule(scheduleId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this schedule?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(scheduleId);
      setError("");
      setSuccess("");

      await api.delete(`/schedules/${scheduleId}`);

      setSuccess("Schedule deleted successfully.");

      await loadSchedules();
    } catch (error) {
      console.error("Schedule deletion error:", error);

      setError(
        error?.response?.data?.detail ||
          "Unable to delete schedule."
      );
    } finally {
      setDeletingId(null);
    }
  }


  function formatTime(hour, minute) {
    const date = new Date();

    date.setHours(Number(hour));
    date.setMinutes(Number(minute));

    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }


  return (
    <div className="page-content">

      <div className="page-header">
        <div>
          <span className="page-eyebrow">
            AUTOMATION
          </span>

          <h1>Schedules</h1>

          <p>
            Create automated schedules for your N1MOX30
            creator intelligence workflows.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadSchedules}
          disabled={loading}
        >
          <RefreshCw
            size={18}
            className={loading ? "spin" : ""}
          />

          Refresh
        </button>
      </div>


      {error && (
        <div className="auth-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}


      {success && (
        <div className="success-message">
          <CheckCircle2 size={18} />
          <span>{success}</span>
        </div>
      )}


      <section className="ai-studio-grid">

        {/* CREATE SCHEDULE */}

        <div className="panel ai-generator-panel">

          <div className="panel-header">
            <div>
              <h3>Create Schedule</h3>

              <p>
                Set when an automated workflow should run.
              </p>
            </div>

            <CalendarDays size={26} />
          </div>


          <form
            className="ai-form"
            onSubmit={createSchedule}
          >

            <label>
              <span>Schedule Name</span>

              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Example: Daily YouTube Analytics"
                required
              />
            </label>


            <label>
              <span>Schedule Type</span>

              <select
                name="schedule_type"
                value={formData.schedule_type}
                onChange={handleChange}
              >
                <option value="daily">
                  Daily
                </option>

                <option value="weekly">
                  Weekly
                </option>

                <option value="monthly">
                  Monthly
                </option>
              </select>
            </label>


            <div className="ai-form-row">

              <label>
                <span>Hour</span>

                <select
                  name="hour"
                  value={formData.hour}
                  onChange={handleChange}
                >
                  {Array.from(
                    { length: 24 },
                    (_, index) => (
                      <option
                        key={index}
                        value={index}
                      >
                        {String(index).padStart(2, "0")}
                      </option>
                    )
                  )}
                </select>
              </label>


              <label>
                <span>Minute</span>

                <select
                  name="minute"
                  value={formData.minute}
                  onChange={handleChange}
                >
                  {[0, 15, 30, 45].map(
                    (minute) => (
                      <option
                        key={minute}
                        value={minute}
                      >
                        {String(minute).padStart(
                          2,
                          "0"
                        )}
                      </option>
                    )
                  )}
                </select>
              </label>

            </div>


            <button
              type="submit"
              className="auth-submit"
              disabled={creating}
            >

              {creating ? (
                <>
                  <LoaderCircle
                    size={19}
                    className="spin"
                  />

                  Creating...
                </>
              ) : (
                <>
                  <Plus size={19} />

                  Create Schedule
                </>
              )}

            </button>

          </form>

        </div>


        {/* AUTOMATION INFORMATION */}

        <div className="panel ai-info-panel">

          <div className="panel-header">
            <div>
              <h3>Automation</h3>

              <p>
                Run creator intelligence workflows
                automatically.
              </p>
            </div>

            <Clock3 size={26} />
          </div>


          <div className="ai-info-hero">

            <CalendarDays
              size={60}
              strokeWidth={1.3}
            />

            <h3>
              Save time with automation
            </h3>

            <p>
              Schedule recurring tasks and keep your
              creator intelligence platform up to date.
            </p>

          </div>

        </div>

      </section>


      {/* EXISTING SCHEDULES */}

      <section className="panel">

        <div className="panel-header">

          <div>
            <h3>
              Your Schedules
            </h3>

            <p>
              Manage your existing automation schedules.
            </p>
          </div>

          <CalendarDays size={24} />

        </div>


        {loading ? (

          <div className="page-loading">

            <LoaderCircle
              size={26}
              className="spin"
            />

            Loading schedules...

          </div>

        ) : schedules.length === 0 ? (

          <div className="empty-state">

            <CalendarDays size={42} />

            <h3>
              No schedules yet
            </h3>

            <p>
              Create your first automation schedule
              above.
            </p>

          </div>

        ) : (

          <div className="schedule-list">

            {schedules.map((schedule) => (

              <div
                className="schedule-item"
                key={schedule.id}
              >

                <div className="schedule-icon">

                  <Clock3 size={20} />

                </div>


                <div className="schedule-details">

                  <strong>
                    {schedule.name}
                  </strong>

                  <span>
                    {schedule.schedule_type || "daily"} â€¢{" "}
                    {formatTime(
                      schedule.hour ?? 0,
                      schedule.minute ?? 0
                    )}
                  </span>

                </div>


                <button
                  className="icon-danger-button"
                  onClick={() =>
                    deleteSchedule(schedule.id)
                  }
                  disabled={
                    deletingId === schedule.id
                  }
                  title="Delete schedule"
                >

                  {deletingId === schedule.id ? (

                    <LoaderCircle
                      size={18}
                      className="spin"
                    />

                  ) : (

                    <Trash2 size={18} />

                  )}

                </button>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}


export default Schedules;


