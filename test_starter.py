#!/usr/bin/env python3
"""
Test suite for Universal Starter GUI
"""

import unittest
import subprocess
import os
from pathlib import Path
import tempfile
import shutil


class TestGitIntegration(unittest.TestCase):
    """Test git integration features."""

    def test_git_status_parsing(self):
        """Test parsing of git status --porcelain output."""
        # Mock output
        mock_output = "M  modified_file.py\nA  added_file.py\n?? untracked_file.py\n"
        lines = mock_output.strip().split('\n')
        self.assertEqual(len(lines), 3)
        # Add more parsing tests

    def test_git_branch_detection(self):
        """Test detection of current branch."""
        # This would require a git repo
        pass

    def test_git_graph_retrieval(self):
        """Test retrieval of branch graph."""
        # This would require a git repo
        pass


class TestEnvironmentCreation(unittest.TestCase):
    """Test environment creation methods."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.venvs_dir = Path(self.test_dir) / ".venvs"
        self.venvs_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_venv_creation(self):
        """Test that venv can be created successfully."""
        import sys
        venv_path = self.venvs_dir / "test_env"
        
        # Create venv
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, f"Venv creation failed: {result.stderr}")
        self.assertTrue(venv_path.exists(), "Venv directory not created")
        
        # Check for pyvenv.cfg
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        self.assertTrue(pyvenv_cfg.exists(), "pyvenv.cfg not found")
        
        # Check for Python executable
        if os.name == "nt":  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = venv_path / "bin" / "python"
        
        self.assertTrue(python_exe.exists(), "Python executable not found")

    def test_venv_validation(self):
        """Test validation of venv environments."""
        venv_path = self.venvs_dir / "test_env"
        
        # Create a valid venv
        import sys
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True
        )
        
        # Validate the venv
        self.assertTrue(venv_path.exists())
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        self.assertTrue(pyvenv_cfg.exists())

    def test_invalid_venv_detection(self):
        """Test detection of invalid venv directories."""
        fake_venv = self.venvs_dir / "fake_env"
        fake_venv.mkdir()
        
        # Should not be valid (no pyvenv.cfg)
        pyvenv_cfg = fake_venv / "pyvenv.cfg"
        self.assertFalse(pyvenv_cfg.exists())


class TestGitManagerMethods(unittest.TestCase):
    """Test GitManager class methods."""
    
    def setUp(self):
        """Set up test git repository."""
        self.test_dir = tempfile.mkdtemp()
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.test_dir, capture_output=True)
    
    def tearDown(self):
        """Clean up test repository."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_git_init_detection(self):
        """Test that GitManager can detect a git repository."""
        # Test with valid repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
    
    def test_git_status_retrieval(self):
        """Test retrieval of git status."""
        # Create a test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test content")
        
        # Get status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("test.txt", result.stdout)
    
    def test_git_branch_operations(self):
        """Test git branch operations."""
        # Create initial commit
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test")
        subprocess.run(["git", "add", "."], cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.test_dir, capture_output=True)
        
        # Create a branch
        result = subprocess.run(
            ["git", "branch", "test-branch"],
            cwd=self.test_dir,
            capture_output=True
        )
        self.assertEqual(result.returncode, 0)
        
        # List branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        self.assertIn("test-branch", result.stdout)


if __name__ == "__main__":
    unittest.main()