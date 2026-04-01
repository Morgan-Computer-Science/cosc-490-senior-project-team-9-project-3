import { useEffect, useState } from "react";

const ProfilePanel = ({ user, onSave, saving }) => {
  const [formData, setFormData] = useState({
    full_name: "",
    major: "",
    year: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) {
      return;
    }

    setFormData({
      full_name: user.full_name ?? "",
      major: user.major ?? "",
      year: user.year ?? "",
    });
  }, [user]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await onSave(formData);
      setMessage("Profile updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update profile.");
    }
  };

  return (
    <section className="panel profile-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Student Profile</p>
          <h2>Keep the advisor grounded in your situation</h2>
        </div>
      </div>

      <div className="profile-summary">
        <div>
          <span className="summary-label">Email</span>
          <strong>{user?.email}</strong>
        </div>
        <div>
          <span className="summary-label">Joined</span>
          <strong>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Unknown"}</strong>
        </div>
      </div>

      <form className="profile-form" onSubmit={handleSubmit}>
        {message ? <p className="form-success">{message}</p> : null}
        {error ? <p className="form-error">{error}</p> : null}

        <label>
          Full name
          <input
            type="text"
            value={formData.full_name}
            onChange={(event) =>
              setFormData((current) => ({ ...current, full_name: event.target.value }))
            }
          />
        </label>

        <label>
          Major
          <select
            value={formData.major}
            onChange={(event) =>
              setFormData((current) => ({ ...current, major: event.target.value }))
            }
          >
            <option value="">Select major</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Information Systems">Information Systems</option>
            <option value="Cloud Computing">Cloud Computing</option>
          </select>
        </label>

        <label>
          Class year
          <select
            value={formData.year}
            onChange={(event) =>
              setFormData((current) => ({ ...current, year: event.target.value }))
            }
          >
            <option value="">Select year</option>
            <option value="Freshman">Freshman</option>
            <option value="Sophomore">Sophomore</option>
            <option value="Junior">Junior</option>
            <option value="Senior">Senior</option>
          </select>
        </label>

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save profile"}
        </button>
      </form>
    </section>
  );
};

export default ProfilePanel;
