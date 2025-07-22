# Branch Protection Setup Guide

This guide explains how to set up branch protection rules for the `master` branch to ensure code quality and prevent direct pushes.

## 🔒 Setting Up Branch Protection

### Step 1: Go to Repository Settings
1. Navigate to your GitHub repository: https://github.com/RoyalPineapple/dyson2mqtt
2. Click on **Settings** tab
3. In the left sidebar, click **Branches**

### Step 2: Add Branch Protection Rule
1. Click **Add rule** or **Add branch protection rule**
2. In the **Branch name pattern** field, enter: `master`
3. Configure the following settings:

### Step 3: Configure Protection Settings

#### ✅ **Require a pull request before merging**
- Check **Require a pull request before merging**
- Check **Require approvals** and set to **1** (or more)
- Check **Dismiss stale PR approvals when new commits are pushed**
- Check **Require review from code owners** (if you have a CODEOWNERS file)

#### ✅ **Require status checks to pass before merging**
- Check **Require status checks to pass before merging**
- Add the following status checks:
  - `Tests and Code Quality / test (3.9)`
  - `Tests and Code Quality / test (3.11)`
  - `Tests and Code Quality / lint`
  - `Tests and Code Quality / security`

#### ✅ **Additional Settings**
- Check **Require branches to be up to date before merging**
- Check **Require conversation resolution before merging**
- Check **Require signed commits** (optional, for extra security)
- Check **Require linear history** (optional, prevents merge commits)

### Step 4: Save the Rule
1. Click **Create** or **Save changes**
2. The rule will now protect the `master` branch

## 🛡️ What This Protects Against

- **Direct pushes to master**: All changes must go through pull requests
- **Unreviewed code**: At least one approval required
- **Failing tests**: All CI checks must pass
- **Outdated branches**: Branches must be up to date with master
- **Unresolved discussions**: All review comments must be resolved

## 🔄 Workflow After Protection

### For Contributors:
1. **Create a feature branch** from `master`
2. **Make your changes** and commit them
3. **Push to your branch** and create a pull request
4. **Wait for CI checks** to complete
5. **Get code review** and address feedback
6. **Merge** once approved and all checks pass

### For Maintainers:
1. **Review pull requests** thoroughly
2. **Ensure CI checks pass** before approving
3. **Merge** only when satisfied with the changes

## 📋 Status Check Details

The following checks must pass before merging:

| Check | Description | Python Versions |
|-------|-------------|-----------------|
| `test` | Unit and integration tests | 3.9, 3.11 |
| `lint` | Code formatting and style | 3.11 |
| `security` | Security analysis | 3.11 |

## 🚨 Troubleshooting

### If CI Checks Fail:
1. **Check the logs** in the Actions tab
2. **Fix the issues** locally
3. **Push the fixes** to your branch
4. **Wait for re-run** of CI checks

### If Branch is Outdated:
1. **Update your branch** with latest master:
   ```bash
   git checkout master
   git pull origin master
   git checkout your-feature-branch
   git rebase master
   git push --force-with-lease
   ```

### If You Need to Bypass (Emergency):
- **Only for critical security fixes**
- **Contact repository maintainers**
- **Use the "Override" option** (if you have admin access)

## 📞 Support

If you encounter issues with branch protection:
1. Check the [GitHub documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
2. Contact repository maintainers
3. Open an issue in the repository

---

**Note**: These settings ensure code quality and prevent accidental merges of broken code. They are essential for maintaining a stable and reliable codebase. 